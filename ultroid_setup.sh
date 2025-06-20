#!/bin/bash

# Script Name: ultroid_setup.sh
# Purpose: Unified setup script for Ultroid UserBot (Docker or Local Python)

# --- Constants & Configuration ---
PYTHON_MIN_VERSION="3.9" # Minimum Python version (e.g., 3.9)
VENV_NAME=".venv"
REQUIREMENTS_FILE="requirements.txt"
ENV_SAMPLE_FILE=".env.sample"
ENV_FILE=".env"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Helper Functions ---

_print_msg() {
    type="$1"
    shift
    message="$*"
    case "$type" in
        info) echo -e "${BLUE}[INFO] $message${NC}" ;;
        warn) echo -e "${YELLOW}[WARN] $message${NC}" ;;
        error) echo -e "${RED}[ERROR] $message${NC}" ;;
        success) echo -e "${GREEN}[SUCCESS] $message${NC}" ;;
        header) echo -e "${GREEN}=== $message ===${NC}" ;;
        *) echo "$message" ;;
    esac
}

_detect_os() {
    os_name=$(uname -s)
    case "$os_name" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "darwin" ;;
        CYGWIN*)    echo "windows_cygwin" ;;
        MINGW*)     echo "windows_mingw" ;;
        *)          echo "unknown:${os_name}" ;;
    esac
}

_command_exists() {
    command -v "$1" >/dev/null 2>&1
}

_check_python_version() {
    local current_version
    local required_version=$1
    local current_major current_minor required_major required_minor

    if ! _command_exists python3; then
        _print_msg error "Python 3 is not installed. Please install Python $required_version or higher."
        return 1
    fi

    current_version=$(python3 -V 2>&1 | awk '{print $2}')

    current_major=$(echo "$current_version" | cut -d. -f1)
    current_minor=$(echo "$current_version" | cut -d. -f2)
    required_major=$(echo "$required_version" | cut -d. -f1)
    required_minor=$(echo "$required_version" | cut -d. -f2)

    if [ "$current_major" -lt "$required_major" ] || { [ "$current_major" -eq "$required_major" ] && [ "$current_minor" -lt "$required_minor" ]; }; then
        _print_msg error "Python version $current_version is installed. Ultroid requires Python $required_version or higher."
        return 1
    fi
    _print_msg success "Python version $current_version found."
    return 0
}

_prompt_user() {
    local prompt_message="$1"
    local var_name="$2"
    local default_value="${3:-}"
    local input

    # Echo the prompt using color codes
    if [ -n "$default_value" ]; then
        echo -e -n "${YELLOW}${prompt_message}${NC} [Default: $default_value]: "
    else
        echo -e -n "${YELLOW}${prompt_message}${NC}: "
    fi

    # Read the input
    read input

    if [ -z "$input" ] && [ -n "$default_value" ]; then
        eval "$var_name=\"$default_value\""
    else
        eval "$var_name=\"$input\""
    fi
}

_prompt_user_sensitive() {
    local prompt_message="$1"
    local var_name="$2"
    local input

    # Echo the prompt using color codes
    echo -e -n "${YELLOW}${prompt_message}${NC}: "

    # Read the input silently
    read -s input </dev/tty
    echo # Newline after sensitive input

    eval "$var_name=\"$input\""
}


# --- Prerequisite Checks ---
_check_prerequisites() {
    _print_msg header "Checking Prerequisites"
    local all_ok=true

    if _command_exists git; then
        _print_msg success "Git is installed."
    else
        _print_msg error "Git is not installed. Please install Git and re-run the script."
        # Add OS-specific install instructions here if desired
        all_ok=false
    fi

    if _check_python_version "$PYTHON_MIN_VERSION"; then
        # Success message already printed by _check_python_version
        if _command_exists pip3; then
             _print_msg success "pip3 is available."
        elif _command_exists pip; then
             _print_msg success "pip is available (will assume it's for Python 3)."
        else
            _print_msg error "pip for Python 3 is not installed. Please install pip."
            all_ok=false
        fi
    else
        all_ok=false
    fi

    if [ "$all_ok" = false ]; then
        _print_msg error "One or more prerequisites are missing. Please install them and try again."
        exit 1
    fi
}

# --- Environment Variable Collection ---
_collect_env_variables() {
    _print_msg header "Collecting Environment Variables"

    if [ -f "$ENV_FILE" ]; then
        _print_msg info "$ENV_FILE already exists."
        read -p "Do you want to (o)verwrite, (u)pdate missing values, or (s)kip? [o/u/s, default: u]: " env_action
        env_action=${env_action:-u}
    else
        _print_msg info "Creating a new $ENV_FILE."
        cp "$ENV_SAMPLE_FILE" "$ENV_FILE" # Start with sample if it exists and target doesn't
        env_action="new"
    fi

    # Define an associative array for defaults and comments if needed for complex logic
    # For now, direct prompts. Load existing values if updating.
    declare -A existing_env_vars
    if [ "$env_action" = "u" ] && [ -f "$ENV_FILE" ]; then
        while IFS='=' read -r key value; do
            # Remove potential surrounding quotes from value
            value="${value%\"}"
            value="${value#\"}"
            value="${value%\'}"
            value="${value#\'}"
            existing_env_vars["$key"]="$value"
        done < <(grep -v '^#' "$ENV_FILE" | grep '=') # Read non-commented lines with '='
    elif [ "$env_action" = "o" ]; then
        > "$ENV_FILE" # Clear the file if overwriting
    fi

    # Helper to get existing or default for prompt
    _get_val() { echo "${existing_env_vars[$1]:-$2}"; }

    API_ID=$(_get_val "API_ID")
    _prompt_user "Enter your API_ID (from my.telegram.org/apps)" API_ID "$API_ID"

    API_HASH=$(_get_val "API_HASH")
    _prompt_user_sensitive "Enter your API_HASH (from my.telegram.org/apps)" API_HASH

    SESSION=$(_get_val "SESSION")
    _prompt_user_sensitive "Enter your SESSION string (Leave blank to generate/get instructions later)" SESSION "$SESSION"

    BOT_TOKEN=$(_get_val "BOT_TOKEN")
    _prompt_user_sensitive "Enter your BOT_TOKEN (Optional, from @BotFather)" BOT_TOKEN "$BOT_TOKEN"

    LOG_CHANNEL=$(_get_val "LOG_CHANNEL" "0")
    _prompt_user "Enter your LOG_CHANNEL ID (Numeric, e.g., -100xxxxxxxx or your User ID)" LOG_CHANNEL "$LOG_CHANNEL"

    OWNER_ID=$(_get_val "OWNER_ID")
    _prompt_user "Enter your OWNER_ID (Your numeric Telegram User ID)" OWNER_ID "$OWNER_ID"

    # Database choice
    DATABASE_TYPE=$(_get_val "DATABASE_TYPE" "redis") # redis, mongo, sql, local
    _print_msg info "Choose your database type:"
    echo "1. Redis (Recommended for Docker, requires Redis server)"
    echo "2. MongoDB (Requires MongoDB server)"
    echo "3. PostgreSQL (Requires PostgreSQL server)"
    echo "4. Local File DB (Simple, no external server needed, default if others unset)"
    read -p "Select database (1-4, default: 1 for Redis if Docker, 4 for Local if not Docker): " db_choice_num

    # Default db_choice_num based on setup type will be handled later
    # For now, let's assume default is redis for this collection part.

    case "$db_choice_num" in
        1) DATABASE_TYPE="redis" ;;
        2) DATABASE_TYPE="mongo" ;;
        3) DATABASE_TYPE="sql" ;;
        4) DATABASE_TYPE="local" ;;
        *) _print_msg warn "Invalid database choice, defaulting to 'redis' for now. This will be refined."
           DATABASE_TYPE="redis" ;; # Default or re-prompt later
    esac

    REDIS_URI=$(_get_val "REDIS_URI")
    REDIS_PASSWORD=$(_get_val "REDIS_PASSWORD")
    MONGO_URI=$(_get_val "MONGO_URI")
    DATABASE_URL=$(_get_val "DATABASE_URL") # For SQL

    if [ "$DATABASE_TYPE" = "redis" ]; then
        _prompt_user "Enter REDIS_URI (e.g., redis://localhost:6379)" REDIS_URI "$REDIS_URI"
        _prompt_user_sensitive "Enter REDIS_PASSWORD (if any)" REDIS_PASSWORD "$REDIS_PASSWORD"
        MONGO_URI="" # Clear other DB vars
        DATABASE_URL=""
    elif [ "$DATABASE_TYPE" = "mongo" ]; then
        _prompt_user "Enter MONGO_URI (e.g., mongodb://user:pass@host:port/dbname)" MONGO_URI "$MONGO_URI"
        REDIS_URI=""
        REDIS_PASSWORD=""
        DATABASE_URL=""
    elif [ "$DATABASE_TYPE" = "sql" ]; then
        _prompt_user "Enter DATABASE_URL (PostgreSQL, e.g., postgresql://user:pass@host:port/dbname)" DATABASE_URL "$DATABASE_URL"
        REDIS_URI=""
        REDIS_PASSWORD=""
        MONGO_URI=""
    else # local
        REDIS_URI=""
        REDIS_PASSWORD=""
        MONGO_URI=""
        DATABASE_URL=""
    fi

    TZ=$(_get_val "TZ" "Asia/Kolkata")
    _prompt_user "Enter your Timezone (e.g., Asia/Kolkata, Europe/London)" TZ "$TZ"

    # Write to .env file
    # This is a simple overwrite. A more sophisticated approach would update existing values.
    {
        echo "API_ID=${API_ID}"
        echo "API_HASH=${API_HASH}"
        echo "SESSION=${SESSION}"
        echo "BOT_TOKEN=${BOT_TOKEN}"
        echo "LOG_CHANNEL=${LOG_CHANNEL}"
        echo "OWNER_ID=${OWNER_ID}"
        echo "TZ=${TZ}"
        if [ "$DATABASE_TYPE" = "redis" ]; then
            echo "REDIS_URI=${REDIS_URI}"
            echo "REDIS_PASSWORD=${REDIS_PASSWORD}"
        elif [ "$DATABASE_TYPE" = "mongo" ]; then
            echo "MONGO_URI=${MONGO_URI}"
        elif [ "$DATABASE_TYPE" = "sql" ]; then
            echo "DATABASE_URL=${DATABASE_URL}"
        fi
        # Add other common optional vars from .env.sample here, prompting if desired
        echo "VCBOT=False" # Example default optional
        echo "ADDONS=False" # Example default optional
    } > "$ENV_FILE"

    _print_msg success "$ENV_FILE has been configured."
}

# --- Main Script Logic ---
main() {
    _print_msg header "Welcome to the Ultroid UserBot Setup Script!"
    _print_msg info "This script will guide you through setting up your fork of Ultroid (github.com/overspend1/Ultroid-fork)."
    echo "You can choose to set it up using Docker or a local Python environment."
    echo "-----------------------------------------------------"

    # Ensure script is run from project root or can find its files
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
    if [ ! -f "$SCRIPT_DIR/$ENV_SAMPLE_FILE" ]; then
        _print_msg error "Could not find $ENV_SAMPLE_FILE. Make sure you are running the script from the Ultroid project root."
        # exit 1 # Potentially allow to continue if user creates .env manually
    else
         cd "$SCRIPT_DIR" # Change to script's directory (project root)
    fi


    DETECTED_OS=$(_detect_os)
    _print_msg info "Detected OS: $DETECTED_OS"

    _check_prerequisites

    echo "-----------------------------------------------------"
    echo "Choose your setup method:"
    echo "1. Docker (Recommended for isolated environment)"
    echo "2. Local Python (Requires Python $PYTHON_MIN_VERSION or higher)"
    read -p "Enter your choice (1 or 2): " setup_choice
    echo "-----------------------------------------------------"

    # Placeholder for setup functions will be replaced below
    # _setup_docker() { _print_msg info "Docker setup chosen (Not yet implemented fully)."; _collect_env_variables; }
    # _setup_local_python() { _print_msg info "Local Python setup chosen (Not yet implemented fully)."; _collect_env_variables; }

_generate_session_docker() {
    _print_msg info "Attempting to generate session string using Docker..."
    if [ ! -f "docker-compose.yml" ]; then
        _print_msg error "docker-compose.yml not found. Cannot generate session with Docker."
        return 1
    fi

    # Ensure session_output directory exists and is writable (Docker user might need this)
    mkdir -p session_output
    # The Dockerfile now runs as non-root 'ultroid'.
    # The session_output volume in docker-compose.yml is /home/ultroid/app/session_output
    # We need to ensure the host ./session_output is writable by this user if it's a new mount.
    # Or, the script inside container should handle permissions if it creates files as root then copies.
    # The current session-gen command `cp *.session session_output/` should work if session_output is WORKDIR/session_output

    _print_msg info "Running Docker session generator. Please follow the prompts."
    _print_msg warn "You will be asked for your API_ID, API_HASH, and phone number by the Telethon script."

    # Temporarily ensure API_ID and API_HASH are available for the session generator container if it needs them from .env
    # The generate-session.sh script's Docker method runs a generic python image with Telethon.
    # The docker-compose profile "session-gen" uses the main Dockerfile.
    # The command `wget -O session.py ... && python3 session.py` does not directly use .env API_ID/HASH.
    # It prompts for them.

    if docker-compose --profile session run --rm session-gen; then
        _print_msg success "Session generation process completed."
        _print_msg info "If successful, your session string was printed to the console and saved in ./session_output."
        _print_msg warn "Please copy the SESSION string from the output above (it's a long string)."
        _prompt_user_sensitive "Paste the generated SESSION string here" SESSION_FROM_GEN
        if [ -n "$SESSION_FROM_GEN" ]; then
            _update_env_var "SESSION" "$SESSION_FROM_GEN" "$ENV_FILE"
            _print_msg success "SESSION string updated in $ENV_FILE."
            return 0
        else
            _print_msg error "No session string was pasted. You might need to run session generation again or enter it manually."
            return 1
        fi
    else
        _print_msg error "Docker session generation failed."
        return 1
    fi
}

_generate_session_if_needed() {
    local session_val
    session_val=$(grep "^SESSION=" "$ENV_FILE" | cut -d'=' -f2-)

    if [ -n "$session_val" ]; then
        _print_msg info "SESSION string already found in $ENV_FILE."
        return 0
    fi

    _print_msg warn "SESSION string is missing."
    echo "How would you like to provide the SESSION string?"
    echo "1. Enter manually"
    echo "2. Generate using Docker (if you chose Docker setup)"
    echo "3. Get instructions for @SessionGeneratorBot (Telegram Bot)"
    read -p "Choose an option [1/2/3, default: 1]: " session_choice
    session_choice=${session_choice:-1}

    case "$session_choice" in
        1)
            _prompt_user_sensitive "Please enter your SESSION string" NEWSESSION
            if [ -n "$NEWSESSION" ]; then
                _update_env_var "SESSION" "$NEWSESSION" "$ENV_FILE"
                _print_msg success "SESSION string updated in $ENV_FILE."
            else
                _print_msg error "No session string entered. Setup might fail."
                return 1
            fi
            ;;
        2)
            # This option should only be presented if Docker setup was chosen.
            # We'll call this function from within _setup_docker or _setup_local_python
            # So, the caller should ensure this option is valid.
            # For now, assume it's called from _setup_docker
            if [ "$SETUP_TYPE" = "docker" ]; then
                 _generate_session_docker || return 1
            else
                _print_msg error "Docker session generation is only available if you chose Docker setup."
                _print_msg info "Please choose another method or restart and select Docker setup."
                return 1
            fi
            ;;
        3)
            _print_msg info "To generate a session string using a Telegram bot:"
            _print_msg info "1. Go to @SessionGeneratorBot on Telegram."
            _print_msg info "2. Follow the bot's instructions."
            _print_msg info "3. Copy the session string provided by the bot."
            _prompt_user_sensitive "Once you have the SESSION string, please paste it here" NEWSESSION
            if [ -n "$NEWSESSION" ]; then
                _update_env_var "SESSION" "$NEWSESSION" "$ENV_FILE"
                _print_msg success "SESSION string updated in $ENV_FILE."
            else
                _print_msg error "No session string entered. Setup might fail."
                return 1
            fi
            ;;
        *)
            _print_msg error "Invalid choice for session string."
            return 1
            ;;
    esac
    return 0
}


_setup_docker() {
    _print_msg header "Starting Docker Setup"
    SETUP_TYPE="docker" # Set context for _generate_session_if_needed

    if ! _command_exists docker; then
        _print_msg error "Docker is not installed. Please install Docker and re-run."
        # Add more specific guidance based on OS if possible
        _print_msg info "Installation guide: https://docs.docker.com/engine/install/"
        exit 1
    fi
    _print_msg success "Docker is installed."

    if ! _command_exists docker-compose && ! docker compose version &>/dev/null; then
        _print_msg error "Docker Compose is not installed. Please install Docker Compose and re-run."
        _print_msg info "Installation guide: https://docs.docker.com/compose/install/"
        exit 1
    fi
    _print_msg success "Docker Compose is installed."

    # Ensure Dockerfile and docker-compose.yml are present
    if [ ! -f "Dockerfile" ] || [ ! -f "docker-compose.yml" ]; then
        _print_msg error "Dockerfile or docker-compose.yml not found. Ensure you are in the project root."
        exit 1
    fi

    # Check if .env.sample exists before calling _collect_env_variables
    if [ ! -f "$ENV_SAMPLE_FILE" ]; then
        _print_msg error "$ENV_SAMPLE_FILE not found. Cannot proceed with environment configuration."
        exit 1
    fi
    _collect_env_variables || { _print_msg error "Failed to configure environment variables."; exit 1; }

    _generate_session_if_needed || { _print_msg error "Session string configuration failed. Please ensure SESSION is set in $ENV_FILE."; exit 1; }

    _print_msg info "Building Docker image(s). This may take some time..."
    if docker-compose build; then
        _print_msg success "Docker image(s) built successfully."
    else
        _print_msg error "Docker image build failed. Please check the output above for errors."
        exit 1
    fi

    _print_msg info "Starting Ultroid services using Docker Compose..."
    if docker-compose up -d; then
        _print_msg success "Ultroid services started successfully in detached mode."
        _print_msg info "You can check the logs using: docker-compose logs -f ultroid"
        _print_msg info "To stop the services, run: docker-compose down"
    else
        _print_msg error "Failed to start Ultroid services. Check 'docker-compose logs ultroid' for details."
        exit 1
    fi
}

_setup_local_python() {
    _print_msg header "Starting Local Python Setup";
    SETUP_TYPE="local"

    # Check Python version again specifically for this path
    if ! _check_python_version "$PYTHON_MIN_VERSION"; then
        exit 1
    fi

    # Check if .env.sample exists
    if [ ! -f "$ENV_SAMPLE_FILE" ]; then
        _print_msg error "$ENV_SAMPLE_FILE not found. Cannot proceed."
        exit 1
    fi
    _collect_env_variables || { _print_msg error "Failed to configure environment variables."; exit 1; }

    # For local Python, session generation via Docker is not an option unless Docker is also installed.
    # _generate_session_if_needed will handle prompting.
    # Modify _generate_session_if_needed to not offer Docker option if SETUP_TYPE="local"
    _generate_session_if_needed || { _print_msg error "Session string configuration failed."; exit 1; }

    _print_msg info "Creating Python virtual environment in '$VENV_NAME'..."
    if python3 -m venv "$VENV_NAME"; then
        _print_msg success "Virtual environment created."
    else
        _print_msg error "Failed to create virtual environment."
        exit 1
    fi

    _print_msg info "Activating virtual environment and installing dependencies..."
    _print_msg warn "This may take a significant amount of time."
    # shellcheck source=/dev/null
    if source "${VENV_NAME}/bin/activate" && pip install -r "$REQUIREMENTS_FILE"; then
        _print_msg success "Dependencies installed successfully."
    else
        _print_msg error "Failed to install dependencies. Check for errors above."
        _print_msg info "You might need to manually activate the venv: 'source $VENV_NAME/bin/activate' and then run 'pip install -r $REQUIREMENTS_FILE'."
        exit 1
    fi

    # Deactivate might not be strictly necessary here as script ends, but good practice
    # Or inform user how to deactivate. For now, leave it active for them to run.

    _print_msg success "Local Python setup complete!"
    _print_msg info "To run Ultroid:"
    _print_msg info "1. If not already active, activate the virtual environment: source $VENV_NAME/bin/activate"
    _print_msg info "2. Start Ultroid: python3 -m pyUltroid"
    _print_msg info "To deactivate the virtual environment later, simply type: deactivate"
}


    case $setup_choice in
        1)
            _setup_docker
            ;;
        2)
            _setup_local_python
            ;;
        *)
            _print_msg error "Invalid choice. Exiting."
            exit 1
            ;;
    esac

    _print_msg success "Ultroid setup process finished."
    _print_msg info "Please review any specific instructions above for your chosen setup type."
}

# --- Entry Point ---
main
