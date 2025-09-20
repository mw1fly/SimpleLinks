## 📝 Summary
<!-- What does this PR do? Why is it needed? -->

- [ ] Migrates link data from CSV to JSON
- [ ] Updates JS loader to read JSON
- [ ] Keeps CSV as backup for now

---

## ✅ Changes
<!-- Bullet points of specific changes in this PR -->

- Added `newlinks.json` sample dataset
- Updated `index.html` loader to use JSON instead of CSV
- Updated Docker config if needed (paths, COPY statements, etc.)
- Adjusted documentation in README

---

## 🔍 Testing
<!-- Steps the reviewer (or future you) can use to test this PR -->

1. Run `docker compose up --build`
2. Visit `http://localhost:8080`
3. Confirm that all links/images load correctly from JSON
4. Confirm old CSV is still present (if needed)

---

## 📸 Screenshots (optional)
<!-- Add screenshots or GIFs to show before/after UI if helpful -->

---

## ⚠️ Notes
<!-- Known issues, follow-up work, or things to improve later -->

- CSV loader still exists, but JSON is now default
- Need to add admin tools for add/delete links in the future
