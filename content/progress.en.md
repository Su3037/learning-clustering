<p class="eyebrow">Progress</p>

## My progress

Your record is kept only in this browser on this device. Export it before switching devices or clearing your browsing data.

```html
<div id="progress-root"><p class="muted">Reading your record…</p></div>
<div class="btn-row" style="margin-top:18px">
<button class="btn primary" type="button" id="export">Export record (JSON)</button>
<label class="btn" for="import">Import record…</label><input id="import" type="file" accept="application/json,.json" class="sr-only">
<button class="btn quiet" type="button" id="clear">Clear this device’s record</button>
</div>
<p id="import-msg" class="small" role="status" aria-live="polite"></p>
```

### About progress on the original student sites

The eight original sites live on different domains, and browsers do not let this course read their storage, so old progress is **not migrated automatically**. Import accepts only JSON exported by this course (schemaVersion 1); it checks the file size, version and challenge ids, and drops fields it does not recognise.
