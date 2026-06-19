# Chrome Snippets

These snippets are intended for the Chrome plugin's Node REPL runtime after `browser` and `tab` are available.

## Extract Comment Records

```js
await tab.playwright.evaluate(() => {
  const items = Array.from(document.querySelectorAll(".comment-item"));
  return items.map((el, i) => {
    const name = el.querySelector(".name")?.textContent?.trim() || "";
    const content =
      el.querySelector(".content .note-text")?.textContent?.trim() ||
      el.querySelector(".content")?.textContent?.trim() ||
      "";
    const date = el.querySelector(".date")?.textContent?.trim() || "";
    const like = el.querySelector(".like .count")?.textContent?.trim() || "";
    const id = el.id || "";
    const isSub = el.classList.contains("comment-item-sub");
    return { i, id, isSub, name, content, date, like };
  }).filter(x => x.content);
});
```

## Find Comment Scroller

```js
await tab.playwright.evaluate(() => {
  return Array.from(document.querySelectorAll(".note-scroller,.comments-container,.comments-el"))
    .map(el => {
      const r = el.getBoundingClientRect();
      return {
        cls: el.className,
        x: r.x,
        y: r.y,
        w: r.width,
        h: r.height,
        scrollTop: el.scrollTop,
        scrollHeight: el.scrollHeight,
        clientHeight: el.clientHeight
      };
    });
});
```

