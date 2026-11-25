# Front page

The front page of zuabi.dev: five portfolio pages standing on a turning wafer. Sideways turns the wafer. Scrolling down unrolls the page in front into the full page. The fold in the bottom corner flips to the archive, where every gallery page, and the CoFlow notice, is a tile on a column and opens where it lives.

This folder is the source. Its name starts with an underscore so that GitHub Pages does not serve it.

## Files

- `template.html`: the stage, the wafer, the archive column and the script.
- `pages/`: the five pages. Each file is a `<style>` block followed by the page's markup.
- `build.py`: puts them together and writes `../index.html`. It reads the gallery's `../config.json` for the archive tiles and expects the pictures and fonts in `../home/`.

## Rebuild

```bash
python3 _front-page/build.py
```

Python 3 only, nothing to install. Do not edit `index.html` by hand: the build overwrites it.

## After adding a gallery page

1. Take a 1280×800 screenshot of the new page and save it as a 640×400 WebP at `home/media/archive/<page-id>.webp`.
2. Run the build. It stops and names the file if a thumbnail is missing.

## Preview

```bash
python3 -m http.server 4174                               # from the repo root, then open http://127.0.0.1:4174/
python3 _front-page/build.py --preview /tmp/front-page    # a standalone copy whose archive links point at the live site
```

## Addresses

- `zuabi.dev/` shows the wafer. `zuabi.dev/#objects` opens one of the five pages, and `zuabi.dev/#archive` opens the archive.
- The gallery is at `zuabi.dev/gallery.html#page-id`. Older links of the form `zuabi.dev/#page-id` are sent on to it.
