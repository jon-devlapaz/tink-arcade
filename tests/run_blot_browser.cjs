const {spawn} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const path = require('node:path');
const [chrome, profile] = process.argv.slice(2);
const browser = spawn(chrome, ['--headless', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--disable-background-networking', '--disable-sync',
  '--disable-component-update', '--disable-extensions', '--metrics-recording-only',
  '--use-mock-keychain', '--password-store=basic',
  '--allow-file-access-from-files', '--host-resolver-rules=MAP * ~NOTFOUND',
  '--remote-debugging-pipe', '--user-data-dir=' + profile],
  {stdio: ['ignore', 'ignore', 'pipe', 'pipe', 'pipe']});
let serial = 0, buffer = '', errors = '';
const pending = new Map(), requests = [];
browser.stderr.on('data', chunk => { errors = (errors + chunk).slice(-4000); });
browser.stdio[4].on('data', chunk => {
  buffer += chunk;
  let end;
  while ((end = buffer.indexOf('\0')) >= 0) {
    const message = JSON.parse(buffer.slice(0, end));
    buffer = buffer.slice(end + 1);
    if (message.id && pending.has(message.id)) {
      const {resolve, reject} = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(JSON.stringify(message.error)));
      else resolve(message.result);
    }
    if (message.method === 'Network.requestWillBeSent') requests.push(message.params.request.url);
  }
});
function call(method, params = {}, sessionId) {
  return new Promise((resolve, reject) => {
    const id = ++serial;
    pending.set(id, {resolve, reject});
    browser.stdio[3].write(JSON.stringify({id, method, params, sessionId}) + '\0');
  });
}
const timeout = setTimeout(() => { console.error('Browser timed out', errors); browser.kill('SIGKILL'); process.exitCode = 1; }, 15000);
(async () => {
  try {
    const {targetId} = await call('Target.createTarget', {url: 'about:blank'});
    const {sessionId} = await call('Target.attachToTarget', {targetId, flatten: true});
    await call('Network.enable', {}, sessionId);
    const url = pathToFileURL(path.join(__dirname, 'blot_browser.html')).href;
    await call('Page.navigate', {url}, sessionId);
    let report;
    for (let i = 0; i < 200; i++) {
      const response = await call('Runtime.evaluate', {expression: 'document.querySelector("#result")?.textContent', returnByValue: true}, sessionId);
      report = response.result.value;
      if (report && report !== 'PENDING') break;
      await new Promise(resolve => setTimeout(resolve, 25));
    }
    if (!report?.startsWith('PASS ')) throw new Error(report || 'No browser assertions executed');
    if (!requests.some(url => url.endsWith('/blot/game.js'))) throw new Error('Missing observed game request');
    if (requests.some(url => !url.startsWith('file:') && url !== 'data:,')) throw new Error('External request: ' + requests.join(', '));
    console.log(report);
    console.log('Observed browser requests: ' + JSON.stringify(requests));
  } catch (error) { console.error(error.stack, errors); process.exitCode = 1; }
  finally { clearTimeout(timeout); browser.kill('SIGTERM'); }
})();
