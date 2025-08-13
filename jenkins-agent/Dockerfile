# Start from an official Jenkins agent image to ensure compatibility.
FROM jenkins/agent:latest-jdk11

# Switch to the root user to install software.
USER root

# --- Install Essential Tools ---
# Update package lists and install essential tools including 'unzip'.
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    unzip && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && apt-get install -y docker-ce-cli

# --- Install Python & Bandit (SAST) ---
RUN apt-get install -y python3 python3-pip && \
    pip3 install bandit

# --- Install Trivy (Container Scanner) ---
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# --- Install SonarQube Scanner ---
ENV SONAR_SCANNER_VERSION=4.7.0.2747
RUN curl -sSLo /tmp/sonar-scanner.zip "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux.zip" && \
    unzip /tmp/sonar-scanner.zip -d /opt && \
    rm /tmp/sonar-scanner.zip && \
    ln -s /opt/sonar-scanner-${SONAR_SCANNER_VERSION}-linux/bin/sonar-scanner /usr/local/bin/sonar-scanner

# --- Install OWASP Dependency-Check ---
ENV DEPENDENCY_CHECK_VERSION=8.4.0
RUN curl -sSLo /tmp/dependency-check.zip "https://github.com/jeremylong/DependencyCheck/releases/download/v${DEPENDENCY_CHECK_VERSION}/dependency-check-${DEPENDENCY_CHECK_VERSION}-release.zip" && \
    unzip /tmp/dependency-check.zip -d /opt && \
    rm /tmp/dependency-check.zip

# --- Final Permissions ---
# Switch back to the 'jenkins' user.
USER jenkins
