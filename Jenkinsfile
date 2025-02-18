pipeline {
    agent {
        docker {
            image 'boisvert/python-build'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }
    environment {
        TOKEN = credentials('alphagamebot-token')
        WEBHOOK = credentials('alphagamebot-webhook')
        JENKINS_NOTIFICATIONS_WEBHOOK = credentials('discord-jenkins-webhook')
        DOCKER_TOKEN = credentials('alphagamedev-docker-token')
        AGB_VERSION = sh(returnStdout: true, script: "cat alphagamebot.json | jq '.VERSION' -cMr").trim()
        COMMIT_MESSAGE = sh(script: 'git log -1 --pretty=%B ${GIT_COMMIT}', returnStdout: true).trim()
    
        GITHUB_TOKEN = credentials('alphagamebot-github-token')
        // MySQL stuff
        MYSQL_HOST = "hubby.internal"
        MYSQL_DATABASE = "alphagamebot"
        MYSQL_USER = "alphagamebot" 
        MYSQL_PASSWORD = credentials('alphagamebot-mysql-password')

        REDDIT_API_SECRET = credentials('alphagamebot-reddit-secret')
        REDDIT_API_ID = "q2WqT5ZGLhdiyjKZO0P9Og"
    }
    stages {
        stage('build') {
            steps {
                // debug if necessary
                // sh 'printenv'

                echo "Building"
                // 8/1/2024 -> No Cache was added because of the fact that Pycord will never update :/
                // ----------> If you know a better way, please make a pull request!
                sh 'docker build -t alphagamedev/alphagamebot:$AGB_VERSION \
                                --build-arg COMMIT_MESSAGE="$COMMIT_MESSAGE" \
                                --build-arg BUILD_NUMBER="$BUILD_NUMBER" \
                                --build-arg BRANCH_NAME="$BRANCH_NAME" \
                                --no-cache .'

            }
        }
        stage('push') {
            steps {
                echo "Pushing image to Docker Hub"
                sh 'echo $DOCKER_TOKEN | docker login -u alphagamedev --password-stdin'
                sh 'docker tag  alphagamedev/alphagamebot:$AGB_VERSION alphagamedev/alphagamebot:latest' // point tag latest to most recent version
                sh 'docker push alphagamedev/alphagamebot:$AGB_VERSION' // push tag latest version
                sh 'docker push alphagamedev/alphagamebot:latest' // push tag latest
                sh 'docker logout'
            }
        }
        stage('deploy') {
            steps {
                // conditionally deploy
                sh "docker container stop alphagamebot || true"
                sh "docker container rm alphagamebot || true"
                sh "docker run -d \
                                -v /mnt/bigga/alphagamebot-cache.sqlite:/docker/request-handler.sqlite \
                                --name alphagamebot \
                                -e TOKEN -e WEBHOOK -e BUILD_NUMBER \
                                -e MYSQL_HOST -e MYSQL_DATABASE -e MYSQL_USER -e MYSQL_PASSWORD -e GITHUB_TOKEN \
                                -e GIT_COMMIT -e REDDIT_API_SECRET -e REDDIT_API_ID --restart=always --net=host \
                                alphagamedev/alphagamebot:$AGB_VERSION -rs" // add alphagamebot flags
            }
        }
    }
    post {
        always {
            script {
                def buildStatus = currentBuild.currentResult ?: 'SUCCESS'
                def discordTitle = "${env.JOB_NAME} - Build #${env.BUILD_NUMBER} ${buildStatus}"
                def discordDescription = "Commit: ${env.GIT_COMMIT}\nBranch: ${env.BRANCH_NAME}\nBuild URL: ${env.BUILD_URL}"
                discordSend(
                    webhookURL: env.JENKINS_NOTIFICATIONS_WEBHOOK,
                    title: discordTitle,
                    description: discordDescription,
                    link: env.BUILD_URL,
                    result: buildStatus
                )
            }
        }
    }
}
