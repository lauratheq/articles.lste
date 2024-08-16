# LSTE Plugin: Article Management and Pagination

This plugin for [Laura's Simple Template Engine (LSTE)](https://github.com/lauratheq/lste) automates the loading, management, and pagination of articles on your static site. It handles the processing of article content, generates excerpts, and supports multi-page article loops with pagination.

## Installation

1. Add the plugin to your LSTE configuration by including it in your `.listerc` file:

    ```ini
    [plugins]
    article-management = lauratheq/article-management.lste
    ```

2. LSTE will automatically download and activate the plugin during the next site generation.

## Configuration

Before using the plugin, you need to configure it in your `lste.conf` file:

```ini
[articles]
active_menu = blog
location = index
articles_per_page = 5
date_format = Y-m-d
```

## How It Works

Since this might be confusing, take a look at `example-full` in the LSTE project for details.

### 1. Article Loading

The plugin scans the specified `articles` directory and loads each article's content, extracting key metadata such as title, date, and excerpt. Articles are sorted by date and stored in the LSTE's plugin_vars for easy access.

### 2. Article Loop and Pagination

The plugin generates a loop of articles on the specified location page (e.g., index). If the number of articles exceeds the `articles_per_page` setting, the plugin automatically creates additional pages and handles pagination links.

* Excerpts and Full Content: The plugin can distinguish between rendering full articles or just excerpts depending on the template used.
* Pagination Links: Previous and next page links are automatically generated for easy navigation between article pages.

### 3. Template Integration

The plugin expects certain placeholders in your templates:

* `{{articles}}`: Replaced with the full content or excerpts of the articles for the first page.
* `{{excerpts}}`: Specifically for rendering excerpts if configured.
* `{{pagination}}`: Replaced with the pagination links.

## Example Workflow

1. Write Articles: Place your markdown articles in the `content/articles/` directory. Each file should be named with a date prefix (e.g., `2024-08-16-my-article.md`).
1. Configure the Plugin: Set up the `config.lste` with your desired settings for article management.
1. Generate Your Site: Run LSTE, and the plugin will automatically handle article loading, excerpt generation, and pagination.
1. Deploy Your Site: The output will include a paginated list of articles with appropriate navigation links.

## Contributing

### Contributor Code of Conduct

Please note that this project is adapting the [Contributor Code of Conduct](https://learn.wordpress.org/online-workshops/code-of-conduct/) from WordPress.org even though this is not a WordPress project. By participating in this project you agree to abide by its terms.

### Basic Workflow

* Grab an issue
* Fork the project
* Add a branch with the number of your issue
* Develop your stuff
* Commit to your forked project
* Send a pull request to the main branch with all the details

Please make sure that you have [set up your user name and email address](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup) for use with Git. Strings such as `silly nick name <root@localhost>` look really stupid in the commit history of a project.

Due to time constraints, you may not always get a quick response. Please do not take delays personally and feel free to remind.

### Workflow Process

* Every new issue gets the label 'Request'
* Every commit must be linked to the issue with following pattern: `#${ISSUENUMBER} - ${MESSAGE}`
* Every PR only contains one commit and one reference to a specific issue
