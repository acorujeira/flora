/* Shell: a small key and value store in IndexedDB, for the last copy of each Sheet read. */
(function () {
  const Shell = (window.Shell = window.Shell || {});
  let dbp = null;
  function open() {
    if (dbp) return dbp;
    dbp = new Promise((resolve, reject) => {
      let req;
      try { req = indexedDB.open("shell-store", 1); } catch (e) { reject(e); return; }
      req.onupgradeneeded = () => req.result.createObjectStore("kv");
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
    dbp.catch(() => { dbp = null; });
    return dbp;
  }
  function run(mode, fn) {
    return open().then(db => new Promise((resolve, reject) => {
      const tx = db.transaction("kv", mode), req = fn(tx.objectStore("kv"));
      tx.oncomplete = () => resolve(req.result);
      tx.onerror = tx.onabort = () => reject(tx.error);
    }));
  }
  Shell.store = {
    /* Both calls settle quietly when storage is blocked: the app still runs, without an offline copy. */
    get: key => run("readonly", s => s.get(key)).catch(() => null),
    set: (key, value) => run("readwrite", s => s.put(value, key)).then(() => true).catch(() => false)
  };
})();
