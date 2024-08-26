<h1 align="center">AlphaGameBot</h1>
<p align="center">A free, open-source multipurpose bot that doesn't suck.</p>
<!-- badges go BRRRR -->
<p align="center">
  <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/AlphaGameDeveloper/AlphaGameBot">
  <img alt="GitHub License" src="https://img.shields.io/github/license/AlphaGameDeveloper/AlphaGameBot?logo=github">
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/AlphaGameDeveloper/AlphaGameBot">
  <img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/alphagamedev/alphagamebot?logo=docker">
  <img alt="Docker Image Version" src="https://img.shields.io/docker/v/alphagamedev/alphagamebot">
  
</p>
<p align="center"> <!-- line 2 for Jenkins! -->
  <img src='https://jenkins.alphagame.dev/buildStatus/icon?job=AlphaGameBot%2FAlphaGameBot+Production%2Fmaster&subject=Production%20Build'>
  <img src="https://jenkins.alphagame.dev/buildStatus/icon?job=AlphaGameBot%2FAlphaGameBot+Nightly%2Fnightly&link=https://alphagame.dev/alphagamebot/nightly&subject=Nightly%20Build" />
</p>
<p align="center">Made by a <b>ENTP</b> with love ❤️</p>

Check out AlphaGameBot's [website](https://alphagame.dev/alphagamebot/)!

## What is AlphaGameBot?
AlphaGameBot is a free and open-source Discord bot.  I got the inspiration to make AlphaGameBot when I was trying to find a good Discord bot that met my high requirements
* **100% Free.**  No Premium version, no purchases, and commands locked behind paywalls, just a functional, cool Discord bot for which we don't have to pay a million bucks.
* **Open-Source.** I am a strong supporter of Open-Source Software, and I would love for the Discord bot that I use to be open-source.
* **Good.**  No, seriously.  As much as I love to see developers make their own small bots, they don't have all the commands we take for granted.  Don't get me wrong--
Everyone should make their own Discord bots!  I love seeing their ideas and bots to play around with.  However, I wanted to make something that any server can use, enormous, big, medium, or small.

That led to the first version of AlphaGameBot.  I am still working on it with nearly every possible moment that I can, *(which is limited, sadly, as I am a high-school student)*
with the intent to make it the amazing bot that we all know it can be.

## How can I add it to my server?
I'm so glad you asked!  AlphaGameBot is available for *anyone* to add to their server.  All required information can be found on AlphaGameBot's webpage [here](https://alphagame.dev/alphagamebot)!

## Can I contribute?
Of course!  Any contribution, big or small, is very much welcome!  Check out my requirements for commits [here](https://alphagame.dev/alphagamebot/faq#can-i-contribute-to-alphagamebot).

## Run the bot
If you do not have a database for the bot, that's fine.  Just use `-n` or `--nodatabase` to tell the bot that, and it'll take care of the rest..

Example: `python main.py -n`
### Example configurations
`python main.py -re .env` - Run the bot WITH database enabled, and also load environment variables from a file called `.env`.

`python main.py -drqe .env` - Run bot in debug mode, but do not track message counts (for **/user stats**)

### Docker :)
Prebuilt images are available on [Docker Hub](https://hub.docker.com/r/alphagamedev/alphagamebot).  More information can be found there.

**QuickStart**: `docker run -d --restart unless-stopped --name some-alphagamebot -e TOKEN="..." alphagamedev/alphagamebot:latest /docker/main.py -nsq`
