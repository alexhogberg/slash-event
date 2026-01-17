# slash-event
[![CodeQL](https://github.com/alexhogberg/slash-event/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/alexhogberg/slash-event/actions/workflows/github-code-scanning/codeql)

This slash command is a utility for creating events with your team. It is built with Slack Bolt, MongoDB, and Google Places API, and comes with an automatic setup.

## Description
The command is built using Slack Bolt for Python and deployed with Fly.io for a simple and scalable setup.

## Prerequisites
You need the following to deploy the solution:
* Docker and Docker Compose (for local development)
* A Fly.io account (for production deployment)
* A Slack workspace where you have admin privileges
* A Google Places API key

### Services
The services used are:
* **MongoDB** - Used for storing information about the events (included in Docker Compose for local development)
* **Google Places API** - Used for suggesting event locations
* **Slack Bolt** - Used for handling Slack commands and events

## Installation

### Using Docker Compose (Recommended)
The easiest way to run the application locally is with Docker Compose, which includes MongoDB:

1. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Slack and Google Places API credentials.

3. Start the application with Docker Compose:
   ```bash
   docker-compose up --build
   ```

This will start both the application and a MongoDB instance. The app will be available at `http://localhost:3000`.

To stop the services:
```bash
docker-compose down
```

To stop and remove all data (including MongoDB data):
```bash
docker-compose down -v
```

### Manual Setup (Without Docker)
Run `./setup.sh` to set up a local virtual environment with all dependencies. After that, run `./local.sh` to start the app locally. Note: You will need to provide your own MongoDB instance.

### Configuration
The configuration is stored in the `.env` file. Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```

The file should contain:
```env
SLACK_CLIENT_ID=your_slack_client_id
SLACK_CLIENT_SECRET=your_slack_client_secret
SLACK_SIGNING_SECRET=your_slack_signing_secret
SLACK_APP_TOKEN=xapp-your-app-token

# For local development with Docker Compose:
MONGO_DB_CONNECTION_STRING=mongodb://mongodb:27017/events

GOOGLE_PLACES_API_KEY=your_google_places_api_key
```

- `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET`: OAuth credentials from your Slack App configuration.
- `SLACK_SIGNING_SECRET`: Used to verify requests from Slack.
- `SLACK_APP_TOKEN`: App-level token for Socket Mode (starts with `xapp-`).
- `MONGO_DB_CONNECTION_STRING`: Connection string for MongoDB. Use `mongodb://mongodb:27017/events` for Docker Compose, or your MongoDB Atlas connection string for production.
- `GOOGLE_PLACES_API_KEY`: Retrieved from the Google Developers Console.

### Deployment
The app is deployed using Fly.io. The deployment process is automated with a GitHub Actions workflow. On every push to the `master` branch:
1. Tests are run using `pytest`.
2. If all tests pass, the app is deployed to Fly.io.

To deploy manually, run:
```bash
flyctl deploy
```

### Notifications
The app includes a daily notification feature that announces events scheduled for the current day. This can be triggered manually or scheduled using a cron job.

## Commands
Once everything is deployed, you can use the `/event` slash command in Slack. The bot provides both private and public messages.

### Available Commands
1. **List Events**:
   ```
   /event list
   ```
   Displays a list of upcoming events.

2. **Create an Event**:
   ```
   /event create
   ```
   Opens a dialog to create a new event. You can specify the date, time, and location.

3. **Suggest a Place**:
   ```
   /event suggest <area>
   ```
   Provides top 5 recommendations from Google Places for the specified area.

4. **Join an Event**:
   ```
   /event join <event_id>
   ```
   Adds you to the participant list of the specified event.

5. **Leave an Event**:
   ```
   /event leave <event_id>
   ```
   Removes you from the participant list of the specified event.

6. **Delete an Event**:
   ```
   /event delete <event_id>
   ```
   Deletes an event. Only the creator of the event can delete it.

### Example Usage
- **List Events**:
   ```
   /event list

   Upcoming events:
   - Monday at 17:30 at The Pub
     Participants: @alexhogberg, @another_user
   ```

- **Create an Event**:
   ```
   /event create
   ```
   Opens a dialog where you can specify the event details.

- **Join an Event**:
   ```
   /event join monday
   ```
   Adds you to the event happening on Monday.

- **Delete an Event**:
   ```
   /event delete monday
   ```
   Deletes the event scheduled for Monday (if you are the creator).

## Future Improvements
- [ ] Add support for recurring events.
- [ ] Improve error handling for edge cases.
- [ ] Add more granular permissions for event management.
- [ ] Enhance the UI for the Slack App Home tab.

## Contributing
Feel free to fork this repository and submit pull requests for new features or bug fixes.

## License
This project is licensed under the MIT License.
