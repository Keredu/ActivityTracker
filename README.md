# ActivityTracker

ActivityTracker is a tool designed to help you record and analyze the time you spend on various activities categorized by topic. With the ability to generate comprehensive reports, you can get a clearer insight into your time distribution.

## Features
- **Real-time Activity Tracking**: Prompt-based system to track your activity start and end times.
- **Detailed Time Reports**: Generate reports that display the time spent on each topic and its activities.

## Getting Started

1. **Run the Tracker**:
    - Command: `python main.py`
    - Description: Track activities in real-time. It prompts for the topic and activity and logs the start and end times. Ensure you have valid topics and activities set up before using.

2. **Clear Registered Activities**:
    - Command: `python clear_activities.py`
    - Description: Clears logged activities while retaining the valid topics and activities.

3. **Generate Time Reports**:
    - Command: `python time_report.py`
    - Description: Displays a report of time allocations for each topic and the activities under them.

4. **Input Random Activities (Testing)**:
    - Command: `python add_random_activities.py`
    - Description: Introduces random activities for testing. Ensure you have valid topics and activities set up prior to using.

## Prerequisites
- Python 3.x
- SQLite

## Contributing

Contributions are welcomed! If you discover any bugs or have suggestions for enhancements, please open an issue or submit a pull request.
