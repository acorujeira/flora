/* Shell: the Sheets adapter. Two calls, the same two the page used through Claude's
   Google Sheets connector, here against the Sheets REST API v4.
     getValues({spreadsheetId, range})            -> {range, values}
     updateValues({spreadsheetId, range, values}) -> the API's answer
   Errors are thrown as {code, message}. */
(function () {
  const Shell = (window.Shell = window.Shell || {});
  const cfg = window.APP_CONFIG || {};
  const API = "https://sheets.googleapis.com/v4/spreadsheets/";
  const err = (code, message) => ({ code, message: message || "" });

  async function call(method, path, body, opts) {
    for (let attempt = 0; ; attempt++) {
      const token = await Shell.auth.token(opts);
      let res;
      try {
        res = await fetch(API + path, {
          method, cache: "no-store",
          headers: Object.assign({ Authorization: "Bearer " + token }, body ? { "Content-Type": "application/json" } : {}),
          body: body ? JSON.stringify(body) : undefined
        });
      } catch (e) { throw err("offline"); }
      if (res.ok) return res.json();
      let message = "";
      try { const j = await res.json(); message = (j && j.error && j.error.message) || ""; } catch (e) {}
      if (res.status === 401) { Shell.auth.drop(); if (attempt === 0) continue; throw err("signin_required", message); }
      if (res.status === 403) throw err("forbidden", message);
      if (res.status === 404) throw err("not_found", message);
      if (res.status === 429) throw err("rate_limited", message);
      if (res.status >= 500) throw err("server_unavailable", message);
      throw err("refused", message);
    }
  }

  Shell.sheets = {
    getValues(a, opts) {
      return call("GET", encodeURIComponent(a.spreadsheetId) + "/values/" + encodeURIComponent(a.range), null, opts);
    },
    updateValues(a, opts) {
      if (!cfg.allowWrites) return Promise.reject(err("read_only"));
      /* USER_ENTERED so a formula stays a formula and a leading apostrophe keeps text as text. */
      return call("PUT", encodeURIComponent(a.spreadsheetId) + "/values/" + encodeURIComponent(a.range) + "?valueInputOption=USER_ENTERED",
        { range: a.range, majorDimension: "ROWS", values: a.values }, opts);
    }
  };
})();
