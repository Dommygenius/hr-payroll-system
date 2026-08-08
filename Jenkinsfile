// HR & Payroll System — Jenkins CI
// Recommended: Multibranch Pipeline or Pipeline job scanning this Jenkinsfile.
// Agent needs Python 3.12+ (or Docker). No Postgres required — SQLite is used for CI by default.

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        DJANGO_SETTINGS_MODULE = 'config.settings'
        SECRET_KEY             = 'jenkins-ci-secret-key-not-for-production'
        DEBUG                 = 'False'
        DATABASE_URL          = 'sqlite:///jenkins_ci.sqlite3'
        REDIS_URL             = 'redis://localhost:6379/0'
        CELERY_BROKER_URL     = 'redis://localhost:6379/1'
        CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONDONTWRITEBYTECODE = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    set -e
                    python3 --version || python --version
                    python3 -m venv .venv || python -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements/dev.txt
                '''
            }
        }

        stage('Migrate') {
            steps {
                sh '''
                    set -e
                    . .venv/bin/activate
                    python manage.py migrate --noinput
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -e
                    . .venv/bin/activate
                    pytest --cov=apps --cov-report=xml --cov-report=term --junitxml=reports/junit.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                    archiveArtifacts artifacts: 'coverage.xml,reports/**', allowEmptyArchive: true
                }
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    set -e
                    . .venv/bin/activate
                    ruff check apps config --ignore E501
                '''
            }
        }
    }

    post {
        success {
            echo 'CI passed — ready to deploy.'
        }
        failure {
            echo 'CI failed — check Test / Lint stages.'
        }
        cleanup {
            cleanWs(deleteDirs: true, notFailBuild: true)
        }
    }
}
