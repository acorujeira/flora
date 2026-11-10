/* Shell: registers the service worker and tells the page when to look for fresh data. */
(function () {
  const Shell = (window.Shell = window.Shell || {});
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      /* When a new version takes over, reload once so it shows straight away.
         Skipped on the very first install, when there was no older version. */
      const hadOld = !!navigator.serviceWorker.controller;
      let reloaded = false;
      navigator.serviceWorker.addEventListener("controllerchange", () => {
        if (!hadOld || reloaded) return;
        reloaded = true;
        location.reload();
      });
      navigator.serviceWorker.register("sw.js").then(() => navigator.serviceWorker.ready).then(reg => {
        /* Once the page is up, fetch any plates not yet kept on the device. */
        if (reg.active) reg.active.postMessage("cache-plates");
        /* Look for a new version each time the app comes back to the foreground. */
        document.addEventListener("visibilitychange", () => {
          if (document.visibilityState === "visible") reg.update().catch(() => {});
        });
      }).catch(() => {});
    });
  }
  /* fn runs when the app returns to the foreground or the connection comes back. */
  Shell.onWake = fn => {
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") fn(); });
    window.addEventListener("online", fn);
  };
})();
