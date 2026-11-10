/* Shell: registers the service worker and tells the page when to look for fresh data. */
(function () {
  const Shell = (window.Shell = window.Shell || {});
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("sw.js").then(() => navigator.serviceWorker.ready).then(reg => {
        /* Once the page is up, fetch any plates not yet kept on the device. */
        if (reg.active) reg.active.postMessage("cache-plates");
      }).catch(() => {});
    });
  }
  /* fn runs when the app returns to the foreground or the connection comes back. */
  Shell.onWake = fn => {
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") fn(); });
    window.addEventListener("online", fn);
  };
})();
