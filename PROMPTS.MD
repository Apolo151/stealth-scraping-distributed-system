# AI Prompts

## Task 1

### Prompt 1
```
Implement the `solve_with_stealth` function:
Steps:
- Human-like "Warm-up"
- Trigger recaptcha
- Extract token and result

Apply stealth scripting practices to achieve a good capatcha score
```

### Prompt 2
```
I want to make my browser automation appear as human as possible. implement the following:
- User Agent Rotation: create a list of realistic user agent strings for different browsersand platforms. randomly pick one each session.

- Viewport Randomization: Prepare a list of common screen resolutions. randomly select one each session

- Timezone Variation: Prepare a list of timezones. Each session should randomly pick one.

- Random Config Function: Write a function that returns a random user agent, viewport, and timezone from the above lists.
```

### Prompt 3
```
I want to make my browser automation appear as human as possible. implement the following functions:
- `human_like_mouse_move`: move mouse in a human-like curved path using bezier curve
- `natural_scroll`: natural scrolling (variable speed, pauses, ...)
- `realistic_delay`: perform human-like delays
```

## Task 2

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

## Task 4

### Prompt 1
```
Polish the system design for a scalable and reliable distributed web scraping system in an organized report according to the following points
``
- microservices producer-consumer architcture

- producer creates tasks & sends them to queue
- Worker nodes consume tasks (stateless containers)
- Spin up extra worker nodes (horiztonal scaling) to handle extra load
- use prometheus (node exporter) to get worker nodes metrics: system heatlh, load, logs
- use SQL database to store state and results

----

Message queue system (RabbitMQ) for task distribution
Worker node architecture with horizontal scaling
SQL Database
Monitoring stack integration points with multiple microservices such as but not limited to
System Health 
System Current Load
System Error Logging
Failover and recovery mechanisms
``
```

### Prompt 2
```
Implement the full architecture diagram using mermaid according to the stated system design document.
```