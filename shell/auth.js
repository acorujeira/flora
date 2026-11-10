/* Shell: Google sign-in in the browser (Google Identity Services, token flow).
   An access token lasts about an hour and there is no refresh token, so the app keeps
   the token on the device until it lapses and asks for a new one when it needs it. */
(function () {
  const Shell = (window.Shell = window.Shell || {});
  const cfg = window.APP_CONFIG || {};
  const KEY = "shell-auth", LOG = "shell-auth-log", GSI = "https://accounts.google.com/gsi/client";
  const QUIET_GAP = 5 * 60 * 1000;   /* at most one unprompted attempt every five minutes */
  const QUIET_MS = 4000;             /* an answer quicker than this needed no tap */
  const err = (code, message) => ({ code, message: message || "" });

  function load() { try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; } }
  function save(o) { try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {} }
  function record(how) {
    try {
      const a = JSON.parse(localStorage.getItem(LOG) || "[]");
      a.push([Date.now(), how]);
      localStorage.setItem(LOG, JSON.stringify(a.slice(-300)));
    } catch (e) {}
  }

  let gsi = null;
  function loadGsi() {
    if (window.google && google.accounts && google.accounts.oauth2) return Promise.resolve();
    if (gsi) return gsi;
    gsi = new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = GSI; s.async = true;
      s.onload = () => resolve();
      s.onerror = () => { s.remove(); gsi = null; reject(err("offline")); };
      document.head.appendChild(s);
    });
    return gsi;
  }

  let pending = null, lastQuiet = 0;
  function request(prompt, quiet) {
    if (pending) return pending;
    const began = Date.now();
    pending = loadGsi().then(() => new Promise((resolve, reject) => {
      const client = google.accounts.oauth2.initTokenClient({
        client_id: cfg.clientId, scope: cfg.scope, prompt,
        callback: r => {
          if (!r || r.error || !r.access_token) { reject(err("signin_required", r && (r.error_description || r.error))); return; }
          const granted = String(r.scope || "").split(" ");
          if (r.scope && !String(cfg.scope).split(" ").every(s => granted.includes(s))) { reject(err("scope_missing")); return; }
          const st = load();
          st.token = r.access_token;
          st.exp = Date.now() + (Number(r.expires_in) || 3600) * 1000 - 60000;
          st.ever = true;
          save(st);
          record(quiet && Date.now() - began < QUIET_MS ? "quiet" : "tap");
          resolve(st.token);
        },
        error_callback: e => {
          if (quiet) record("blocked");
          reject(err("signin_required", e && e.type));
        }
      });
      client.requestAccessToken();
    })).finally(() => { pending = null; });
    return pending;
  }

  Shell.auth = {
    configured: () => !!cfg.clientId,
    everSignedIn: () => !!load().ever,
    hasToken: () => { const s = load(); return !!(s.token && s.exp > Date.now()); },
    /* Returns an access token, or throws {code}. Without `interactive` it only tries the
       unprompted route, which Google or the browser may refuse; the caller then shows a
       sign-in control, and a press on that control calls this with interactive: true. */
    async token(opts) {
      opts = opts || {};
      const s = load();
      if (!opts.choose && s.token && s.exp > Date.now()) return s.token;
      if (!cfg.clientId) throw err("not_configured");
      if (navigator.onLine === false) throw err("offline");
      if (opts.interactive) return request(opts.choose ? "select_account" : "", false);
      if (!s.ever || Date.now() - lastQuiet < QUIET_GAP) throw err("signin_required");
      lastQuiet = Date.now();
      return request("", true);
    },
    /* Drop a token Google has refused. */
    drop() { const s = load(); delete s.token; delete s.exp; save(s); },
    /* For the report on how often sign-in needed a tap. */
    stats(days) {
      let a = []; try { a = JSON.parse(localStorage.getItem(LOG) || "[]"); } catch (e) {}
      const from = Date.now() - (days || 7) * 86400000, out = { quiet: 0, tap: 0, blocked: 0 };
      a.forEach(([t, how]) => { if (t >= from && how in out) out[how]++; });
      return out;
    }
  };
})();
