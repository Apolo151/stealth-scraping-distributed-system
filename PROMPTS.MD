# AI Prompts


## Task 3

### Prompt 1
```
Implement the `get_base64_from_url` function: it should download an image and convert it to a base64 string
```

### Prompt 2
```
Implement the `scrape_images` function: it should contain two steps:

- Scrap all images as base64 encoded & save them to file "allimages.json"
- Scrap only the 9 Images as base64 encoded visible to humans and save them to file "visible_images_only.json"
```

### Prompt 3
```
update the `scrape_images` function: the second step should Scrap only the 9 Images visible to humans as base64 encoded

Steps:
- for each image, get the direct `div` parent of the image
- perform basic visibility check (e.g., display: none)
- check that it is at the top (not element on top of it)
```

### Prompt 4
```
update the `scrape_text` function: it should scrape human visible text only

For each text:
- perform basic visibility check (e.g., display: none)
- check that it is at the top (not element on top of it)
```