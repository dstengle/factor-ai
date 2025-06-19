# Factor I: Codebase - Detailed Patterns and Anti-Patterns

## Core Principle
**One codebase tracked in revision control, many deploys**

## Table of Contents
1. [Technology-Neutral Guidance](#technology-neutral-guidance)
2. [JavaScript/Node.js Examples](#javascriptnodejs-examples)
3. [Python Examples](#python-examples)
4. [Java Examples](#java-examples)
5. [Ruby Examples](#ruby-examples)
6. [Go Examples](#go-examples)
7. [Common Scenarios and Solutions](#common-scenarios-and-solutions)

---

## Technology-Neutral Guidance

### What This Means

A twelve-factor app maintains a strict one-to-one relationship between:
- **One codebase**: A single repository containing all the code for one application
- **Many deploys**: Multiple running instances (development, staging, production) all deployed from the same codebase

### Patterns ✓

#### 1. Single Repository Per Application
- Each application has its own dedicated repository
- Clear boundaries between different applications
- Repository contains all code needed to run the application

#### 2. Version Control Everything
- All application code is tracked in version control (Git, Mercurial, SVN)
- Configuration templates and documentation included
- Infrastructure as Code (IaC) can be in same repo or separate

#### 3. Multiple Deployments from Same Code
- Development, staging, and production all use the same codebase
- Differences between environments handled through configuration, not code
- Any developer can trace production code back to a specific commit

#### 4. Shared Code via Libraries
- Common functionality extracted into versioned libraries/packages
- Libraries distributed through language-specific package managers
- Each app explicitly declares its dependency on shared libraries

### Anti-Patterns ✗

#### 1. Multiple Apps in One Repository
- Don't combine frontend, backend, and admin apps in one repo
- Avoid "monorepo" unless using proper tooling (Nx, Lerna, Bazel)
- Each deployable unit should have its own repository

#### 2. Copy-Paste Code Sharing
- Never copy code between projects
- Don't maintain duplicate versions of the same functionality
- Avoid "vendoring" your own code between projects

#### 3. Environment-Specific Branches
- No "production" branch with production-only code
- No "staging" branch with test-specific modifications
- Don't use branches to manage environment differences

#### 4. Untracked Files
- All code must be in version control
- No deployment depending on files outside the repository
- Configuration templates must be tracked (not the actual config)

#### 5. Deploy-Time Code Changes
- No editing files on production servers
- No git operations during deployment (except clone/checkout)
- Build artifacts should be immutable

---

## JavaScript/Node.js Examples

### ✅ GOOD: Single Application Repository

```
my-node-app/
├── .git/
├── .gitignore
├── package.json
├── package-lock.json
├── README.md
├── src/
│   ├── index.js
│   ├── routes/
│   │   ├── auth.js
│   │   ├── users.js
│   │   └── products.js
│   ├── models/
│   │   ├── User.js
│   │   └── Product.js
│   ├── services/
│   │   ├── database.js
│   │   ├── cache.js
│   │   └── email.js
│   └── utils/
│       └── validation.js
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/
│   └── migrate.js
└── .env.example
```

**package.json:**
```json
{
  "name": "my-node-app",
  "version": "1.0.0",
  "description": "Single application with clear boundaries",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "migrate": "node scripts/migrate.js"
  },
  "dependencies": {
    "express": "4.18.2",
    "pg": "8.11.0",
    "@mycompany/auth-lib": "2.1.0"
  }
}
```

### ✅ GOOD: Shared Library Approach

**Repository 1: Shared Authentication Library**
```
auth-lib/
├── .git/
├── package.json
├── src/
│   ├── index.js
│   ├── jwt.js
│   └── middleware.js
└── tests/
```

**auth-lib/package.json:**
```json
{
  "name": "@mycompany/auth-lib",
  "version": "2.1.0",
  "main": "src/index.js",
  "publishConfig": {
    "registry": "https://npm.mycompany.com"
  }
}
```

**Repository 2: Main Application Using Library**
```json
{
  "name": "my-app",
  "dependencies": {
    "@mycompany/auth-lib": "2.1.0"
  }
}
```

### ✅ GOOD: Multiple Deploys Configuration

**.env.example (tracked):**
```bash
# This file documents required environment variables
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:pass@localhost/myapp
REDIS_URL=redis://localhost:6379
API_KEY=your-api-key-here
```

**Deployment configurations (not in repo):**
```bash
# development.env (local machine)
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://dev:dev@localhost/myapp_dev

# staging.env (staging server)
NODE_ENV=staging
PORT=3000
DATABASE_URL=postgresql://user:pass@staging-db/myapp_staging

# production.env (production server)
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://user:pass@prod-db/myapp_prod
```

### ❌ BAD: Multiple Apps in One Repository

```
monorepo/
├── frontend/
│   ├── package.json
│   ├── src/
│   └── public/
├── backend/
│   ├── package.json
│   └── src/
├── admin-panel/
│   ├── package.json
│   └── src/
└── mobile-app/
    ├── package.json
    └── src/
```

**Why it's bad:**
- Can't deploy apps independently
- Different apps have different deployment cycles
- Permissions and access control become complex
- CI/CD pipelines become complicated

### ❌ BAD: Environment Branches

```bash
# NEVER DO THIS
git branch
  main
  development  # Different code for dev
  staging      # Different code for staging  
  production   # Different code for production

# Each branch has environment-specific code changes
git checkout production
# Contains hardcoded production URLs, removed debug code, etc.
```

### ❌ BAD: Copy-Paste Code Sharing

```
app-1/
├── src/
│   └── utils/
│       └── auth.js  # Copied from another project

app-2/
├── src/
│   └── utils/
│       └── auth.js  # Same code, manually kept in sync

app-3/
├── src/
│   └── utils/
│       └── auth.js  # Diverged over time, has bugs fixed that others don't
```

### ✅ Alternative: Proper Monorepo with Tooling

If you must use a monorepo, use proper tooling:

**With Nx:**
```
my-nx-workspace/
├── .git/
├── nx.json
├── package.json
├── apps/
│   ├── web-app/
│   ├── mobile-app/
│   └── api/
├── libs/
│   ├── ui-components/
│   ├── auth/
│   └── data-models/
└── tools/
```

**With Lerna:**
```
my-lerna-monorepo/
├── .git/
├── lerna.json
├── package.json
├── packages/
│   ├── app-frontend/
│   │   └── package.json
│   ├── app-backend/
│   │   └── package.json
│   └── shared-utils/
│       └── package.json
```

---

## Python Examples

### ✅ GOOD: Django Application Structure

```
django-app/
├── .git/
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── manage.py
├── myapp/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── products/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   └── common/
│       └── utils.py
├── static/
├── templates/
└── .env.example
```

### ✅ GOOD: Flask Microservice

```
flask-service/
├── .git/
├── .gitignore
├── setup.py
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── resources.py
│   ├── models/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── migrations/
└── run.py
```

**setup.py for shared libraries:**
```python
from setuptools import setup, find_packages

setup(
    name='mycompany-common',
    version='1.2.3',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'pydantic>=1.10.0',
    ],
    author='MyCompany',
    description='Shared utilities for MyCompany services',
    url='https://github.com/mycompany/python-common',
)
```

### ❌ BAD: Mixed Concerns Repository

```
python-projects/
├── website/
│   ├── django_app.py
│   └── templates/
├── data_pipeline/
│   ├── etl.py
│   └── requirements.txt
├── ml_model/
│   ├── train.py
│   └── requirements.txt
├── scripts/
│   ├── deployment.py
│   └── backup.py
└── shared_code/  # Copy-pasted between projects
    └── utils.py
```

### ❌ BAD: Environment-Specific Code

```python
# settings.py - WRONG APPROACH
import socket

if 'prod' in socket.gethostname():
    DEBUG = False
    DATABASE = 'postgresql://prod-db/app'
    # Production-only code
    from .prod_specific import *
else:
    DEBUG = True
    DATABASE = 'sqlite:///local.db'
    # Development-only code
    INSTALLED_APPS.append('debug_toolbar')
```

---

## Java Examples

### ✅ GOOD: Spring Boot Application

```
spring-boot-app/
├── .git/
├── .gitignore
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── mycompany/
│   │   │           └── app/
│   │   │               ├── Application.java
│   │   │               ├── controllers/
│   │   │               ├── services/
│   │   │               ├── repositories/
│   │   │               └── models/
│   │   └── resources/
│   │       ├── application.properties
│   │       ├── application-dev.properties
│   │       └── application-prod.properties
│   └── test/
│       └── java/
└── README.md
```

**pom.xml for shared library:**
```xml
<project>
    <groupId>com.mycompany</groupId>
    <artifactId>common-utils</artifactId>
    <version>1.2.3</version>
    <packaging>jar</packaging>
    
    <distributionManagement>
        <repository>
            <id>mycompany-nexus</id>
            <url>https://nexus.mycompany.com/repository/maven-releases/</url>
        </repository>
    </distributionManagement>
</project>
```

### ✅ GOOD: Gradle Multi-Module (Single App)

```
gradle-app/
├── .git/
├── settings.gradle
├── build.gradle
├── gradle.properties
├── app/
│   ├── build.gradle
│   └── src/main/java/
├── core/
│   ├── build.gradle
│   └── src/main/java/
└── web/
    ├── build.gradle
    └── src/main/java/
```

**settings.gradle:**
```gradle
rootProject.name = 'my-application'
include 'app', 'core', 'web'
```

### ❌ BAD: Multiple Applications Mixed

```
java-projects/
├── customer-api/
│   └── src/
├── admin-portal/
│   └── src/
├── batch-jobs/
│   └── src/
└── shared/  # Wrong way to share code
    └── src/
        └── com/mycompany/common/
```

---

## Ruby Examples

### ✅ GOOD: Rails Application

```
rails-app/
├── .git/
├── .gitignore
├── .ruby-version
├── Gemfile
├── Gemfile.lock
├── config.ru
├── Rakefile
├── app/
│   ├── controllers/
│   ├── models/
│   ├── views/
│   └── services/
├── config/
│   ├── application.rb
│   ├── database.yml
│   ├── routes.rb
│   └── environments/
├── db/
│   ├── migrate/
│   └── schema.rb
├── lib/
├── spec/
└── .env.example
```

### ✅ GOOD: Ruby Gem for Shared Code

```
my-company-gem/
├── .git/
├── my_company_gem.gemspec
├── Gemfile
├── lib/
│   ├── my_company_gem.rb
│   └── my_company_gem/
│       ├── version.rb
│       └── utilities.rb
├── spec/
└── README.md
```

**my_company_gem.gemspec:**
```ruby
Gem::Specification.new do |spec|
  spec.name          = "my_company_gem"
  spec.version       = "1.2.3"
  spec.authors       = ["MyCompany"]
  spec.summary       = "Shared utilities"
  spec.files         = Dir["lib/**/*"]
  spec.require_paths = ["lib"]
  
  spec.add_dependency "activesupport", ">= 6.0"
end
```

### ❌ BAD: Environment-Specific Branches

```ruby
# On 'production' branch - WRONG
class ApplicationController < ActionController::Base
  # Production-only security headers
  before_action :set_production_headers
  
  def set_production_headers
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
  end
end

# On 'development' branch - WRONG  
class ApplicationController < ActionController::Base
  # Debug mode for development
  before_action :enable_profiler
end
```

---

## Go Examples

### ✅ GOOD: Go Module Structure

```
go-service/
├── .git/
├── go.mod
├── go.sum
├── main.go
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handlers/
│   ├── models/
│   └── services/
├── pkg/
│   └── utils/
├── configs/
│   └── config.example.yaml
└── deployments/
    └── docker/
        └── Dockerfile
```

**go.mod:**
```go
module github.com/mycompany/my-service

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/mycompany/shared-lib v1.2.3
)
```

### ✅ GOOD: Shared Go Library

```
go-shared-lib/
├── .git/
├── go.mod
├── auth/
│   ├── jwt.go
│   └── middleware.go
├── database/
│   └── connection.go
└── utils/
    └── validation.go
```

**Using the shared library:**
```go
import (
    "github.com/mycompany/shared-lib/auth"
    "github.com/mycompany/shared-lib/utils"
)
```

### ❌ BAD: Vendor Your Own Code

```
my-go-app/
├── vendor/
│   └── mycompany/
│       └── common/  # Don't vendor your own organization's code
│           └── utils.go
├── main.go
└── go.mod
```

---

## Common Scenarios and Solutions

### Scenario 1: Need to Share Code Between Services

❌ **Wrong Way:**
- Copy files between repositories
- Use git submodules for your own code
- Create a "shared" folder in multiple repos

✅ **Right Way:**
- Extract to a versioned library
- Publish to package registry (npm, PyPI, Maven Central, etc.)
- Each service declares dependency with specific version

### Scenario 2: Different Features for Different Environments

❌ **Wrong Way:**
```javascript
if (process.env.NODE_ENV === 'production') {
  // Production-only feature
  app.use(advancedAnalytics);
} else {
  // Development-only feature
  app.use(debugToolbar);
}
```

✅ **Right Way:**
```javascript
// Use feature flags
if (process.env.FEATURE_ANALYTICS === 'true') {
  app.use(advancedAnalytics);
}

if (process.env.FEATURE_DEBUG_TOOLBAR === 'true') {
  app.use(debugToolbar);
}
```

### Scenario 3: Client Wants Custom Features

❌ **Wrong Way:**
- Create client-specific branches
- Fork the codebase for each client
- Add client name checks in code

✅ **Right Way:**
- Use feature flags for client features
- Create plugin/extension system
- Use configuration to enable client features

### Scenario 4: Migrating from Monolith to Microservices

✅ **Gradual Approach:**
1. Keep monolith in one repository
2. Extract services one at a time to new repositories
3. Share code through libraries, not copying
4. Each service gets its own deployment pipeline

### Scenario 5: Managing Related Projects

✅ **Options for Related But Separate Apps:**

**Option 1: Separate Repositories**
```
github.com/mycompany/
├── web-frontend/
├── mobile-app/
├── backend-api/
└── admin-dashboard/
```

**Option 2: Organization with Clear Boundaries**
```
github.com/mycompany/
├── services/
│   ├── user-service/
│   ├── order-service/
│   └── notification-service/
├── libraries/
│   ├── auth-lib/
│   └── common-utils/
└── applications/
    ├── web-app/
    └── mobile-app/
```

### Key Takeaways

1. **One App = One Repo**: Each deployable application gets its own repository
2. **Share Through Packages**: Use your language's package manager for shared code
3. **Same Code Everywhere**: Development, staging, and production run the same code
4. **Config Changes Behavior**: Environment differences come from configuration, not code
5. **Track Everything**: All code needed to run the app must be in version control

### Quick Checklist

- [ ] Does each deployable unit have its own repository?
- [ ] Is all code tracked in version control?
- [ ] Are you using the same codebase for all environments?
- [ ] Is shared code distributed as versioned packages?
- [ ] Can you trace any running instance back to a specific commit?
- [ ] Are you avoiding environment-specific branches or code?