Contributing to TTA
===================

We welcome contributions to the Therapeutic Text Adventure (TTA) platform! This guide will help you get started with contributing to the project.

Getting Started
---------------

Before you begin contributing, please:

1. **Read the Documentation**: Familiarize yourself with the project by reading the :doc:`overview` and :doc:`getting-started` guides.

2. **Set Up Development Environment**: Follow the setup instructions in :doc:`getting-started`.

3. **Join the Community**: Participate in `GitHub Discussions <https://github.com/theinterneti/TTA/discussions>`_ to connect with other contributors.

Ways to Contribute
------------------

Code Contributions
~~~~~~~~~~~~~~~~~~

- **Bug Fixes**: Help fix reported issues
- **Feature Development**: Implement new features
- **Performance Improvements**: Optimize existing code
- **Test Coverage**: Add tests for untested code

Documentation
~~~~~~~~~~~~~

- **API Documentation**: Improve docstrings and API docs
- **User Guides**: Write tutorials and how-to guides
- **Developer Documentation**: Enhance development guides
- **Examples**: Create example applications and use cases

Quality Assurance
~~~~~~~~~~~~~~~~~

- **Bug Reports**: Report issues you encounter
- **Testing**: Help test new features and releases
- **Code Review**: Review pull requests from other contributors
- **Security Audits**: Help identify security vulnerabilities

Development Workflow
--------------------

1. Fork and Clone
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Fork the repository on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/TTA.git
   cd TTA

   # Add upstream remote
   git remote add upstream https://github.com/theinterneti/TTA.git

2. Create a Branch
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create a new branch for your feature
   git checkout -b feature/your-feature-name

   # Or for bug fixes
   git checkout -b fix/issue-description

3. Make Changes
~~~~~~~~~~~~~~~

- Write clean, well-documented code
- Follow the project's coding standards
- Add tests for new functionality
- Update documentation as needed

4. Test Your Changes
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run the full test suite
   uv run pytest tests/

   # Run code quality checks
   uv run pre-commit run --all-files

   # Test with coverage
   uv run pytest tests/ --cov=src --cov-report=html

5. Commit Your Changes
~~~~~~~~~~~~~~~~~~~~~~

We use conventional commits for clear commit messages:

.. code-block:: bash

   # Examples of good commit messages
   git commit -m "feat: add user authentication system"
   git commit -m "fix: resolve database connection timeout"
   git commit -m "docs: update API documentation"
   git commit -m "test: add integration tests for user service"

6. Push and Create Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Push your branch
   git push origin feature/your-feature-name

   # Create a pull request on GitHub

Coding Standards
----------------

Code Style
~~~~~~~~~~

- **Formatting**: Use Black for code formatting
- **Import Sorting**: Use isort for import organization
- **Linting**: Use Ruff for linting
- **Type Hints**: Use type hints for all functions and methods

.. code-block:: python

   # Good example
   def calculate_risk_score(
       anxiety_level: int,
       depression_level: int,
       history: Optional[List[str]] = None
   ) -> float:
       """Calculate therapeutic risk score.

       Args:
           anxiety_level: Anxiety level (0-10)
           depression_level: Depression level (0-10)
           history: Optional list of historical factors

       Returns:
           Risk score as a float between 0.0 and 1.0
       """
       # Implementation here
       pass

Documentation Standards
~~~~~~~~~~~~~~~~~~~~~~~

- **Docstrings**: Use Google-style docstrings
- **Type Information**: Include parameter and return types
- **Examples**: Provide usage examples where helpful
- **Error Handling**: Document exceptions that may be raised

.. code-block:: python

   def process_user_input(input_text: str) -> ProcessedInput:
       """Process and validate user input.

       This function sanitizes user input and extracts relevant
       therapeutic information for further processing.

       Args:
           input_text: Raw user input text

       Returns:
           ProcessedInput object containing sanitized and structured data

       Raises:
           ValidationError: If input contains invalid or harmful content
           ProcessingError: If input cannot be processed

       Example:
           >>> processed = process_user_input("I'm feeling anxious today")
           >>> print(processed.sentiment)
           'negative'
       """
       pass

Testing Standards
~~~~~~~~~~~~~~~~~

- **Test Coverage**: Aim for 80%+ coverage on new code
- **Test Types**: Write unit, integration, and end-to-end tests as appropriate
- **Test Naming**: Use descriptive test names that explain what is being tested
- **Test Organization**: Group related tests in classes

.. code-block:: python

   class TestUserAuthentication:
       """Tests for user authentication functionality."""

       def test_valid_credentials_returns_jwt_token(self):
           """Test that valid credentials return a JWT token."""
           # Test implementation
           pass

       def test_invalid_credentials_raises_authentication_error(self):
           """Test that invalid credentials raise AuthenticationError."""
           # Test implementation
           pass

Pull Request Guidelines
-----------------------

Before Submitting
~~~~~~~~~~~~~~~~~

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated if needed
- [ ] Commit messages follow conventional commit format

Pull Request Description
~~~~~~~~~~~~~~~~~~~~~~~~

Please include in your PR description:

1. **Summary**: Brief description of changes
2. **Motivation**: Why this change is needed
3. **Changes**: Detailed list of modifications
4. **Testing**: How the changes were tested
5. **Screenshots**: If UI changes are involved

Example PR template:

.. code-block:: markdown

   ## Summary
   Add user authentication system with JWT tokens

   ## Motivation
   Users need to be able to securely authenticate to access therapeutic sessions

   ## Changes
   - Add JWT authentication middleware
   - Create user login/logout endpoints
   - Add password hashing utilities
   - Update database schema for user accounts

   ## Testing
   - Added unit tests for authentication functions
   - Added integration tests for login/logout flow
   - Tested manually with Postman

   ## Checklist
   - [x] Tests pass
   - [x] Documentation updated
   - [x] Code follows style guidelines

Review Process
~~~~~~~~~~~~~~

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: Maintainers review code for quality and correctness
3. **Testing**: Changes are tested in staging environment
4. **Approval**: At least one maintainer approval required
5. **Merge**: Changes are merged into main branch

Issue Reporting
---------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, please include:

- **Environment**: OS, Python version, dependency versions
- **Steps to Reproduce**: Clear steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Error Messages**: Full error messages and stack traces
- **Additional Context**: Any other relevant information

Feature Requests
~~~~~~~~~~~~~~~~

When requesting features, please include:

- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should this be implemented?
- **Alternatives**: What alternatives have you considered?
- **Use Cases**: How would this feature be used?
- **Priority**: How important is this feature?

Security Issues
~~~~~~~~~~~~~~~

**Do not report security vulnerabilities in public issues.**

Instead, please email security concerns to: security@tta-platform.org

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~~

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be Respectful**: Treat all community members with respect
- **Be Inclusive**: Welcome newcomers and help them get started
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Patient**: Remember that everyone is learning

Communication
~~~~~~~~~~~~~

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code review and technical discussion
- **Email**: For security issues and private matters

Recognition
-----------

Contributors are recognized in several ways:

- **Contributors File**: Listed in CONTRIBUTORS.md
- **Release Notes**: Mentioned in release announcements
- **GitHub**: Contributor statistics and badges
- **Community**: Recognition in community discussions

Getting Help
------------

If you need help with contributing:

- **Documentation**: Check this guide and other documentation
- **Discussions**: Ask questions in GitHub Discussions
- **Issues**: Look for issues labeled "good first issue"
- **Mentorship**: Experienced contributors are happy to help newcomers

Thank you for contributing to TTA! Your contributions help make therapeutic support more accessible and effective for everyone.
