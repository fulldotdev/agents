# Notion Posts

Read this reference when a task uses the central Posts database.

## Location

- Database: [Posts](https://www.notion.so/33a669ecf07b471a984e717b50a65e4e)
- Database ID: `33a669ec-f07b-471a-984e-717b50a65e4e`
- Current data source ID: `1d761b93-c1de-4b8a-a29e-6bb7ea42c424`

Read the live schema before exact property writes because Notion fields and option IDs can change.

## Current properties

- `Name`: title
- `Status`: `Idea`, `Draft`, `Scheduled`, or `Published`
- `Type`: `Text`, `Image`, `Carousel`, or `Video`
- `Publish date`: scheduled or actual publication date
- `Tasks`: relation to the source or delivery Task

Do not mark a Post `Scheduled` without a real schedule. Do not mark it `Published` until the public post and URL are verified.

## Page body

Keep these sections in this order:

1. `Caption`: canonical caption
2. `Platform captions`: channel-specific variants when needed
3. `Media`: format, order, source links, and uploaded media
4. `Published URLs`: verified public links after publishing

Use the Notion file upload API for binary media. Preserve the requested order and read back the page after writes. For important final assets, download the Notion files again and compare them with the approved local files.

Creating or editing a Post is not permission to publish it. Obtain explicit approval immediately before any external scheduling or publication action.
