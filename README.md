# Getting Started with the Mule Back-End Repository

## Cloning the Repository and getting started

Open a new instance of terminal and navigate directory where you want to store the repository. Run the following:

### `git clone https://github.com/JohnMerlino1235/MULE.git`

# Working on a new ticket - Developer Runbook

We will be assigning tickets for each new feature that we will develop. To work on an assigned ticket from our project found [here](https://lams-eece.atlassian.net/jira/software/c/projects/LAM/boards/2), please do the following:

Switch to the main branch:
### `git checkout main`

Pull the most recent version of the main branch:
### `git pull -r origin main`

Create a new branch based on the ticket you are working on:
### `git checkout -b ${TICKET_NAME}`

For example, if I was working on the LAM-1 ticket, I would do the following:
### `git checkout -b LAM-1`

# Committing Code

Add all necessary files that should be committed:
### `git add .`

Commit the added files with a message corresponding to the ticket description:
### `git commit -m "${TICKET_DESCRIPTION}"`

For example, if I was working on [this](https://lams-eece.atlassian.net/jira/software/c/projects/LAM/boards/2?modal=detail&selectedIssue=LAM-1) ticket I would add the following commit message:
### `git commit -m "[FE] - Login Page Implementation"`

Push the commit to your branch:
### `git push`

Create a pull request merging your newly created branch into main. Alert the software channel in discord of the planned changes so someone can look over your changes to provide feedback / accept the request and merge into main.

Documentation on pull requests found [here](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request)


