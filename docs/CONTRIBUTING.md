# Contributing to The Mnemosyne Protocol

Thank you for your interest in contributing to The Mnemosyne Protocol! We're building trustable AI through scientific validation and open standards, and we need your help.

## Ways to Contribute

### 1. For Researchers
- **Validate hypotheses**: Help prove or disprove our experimental features
- **Design studies**: Create validation protocols for Track 2 features
- **Analyze data**: Help interpret metrics from experimental plugins
- **Peer review**: Review our methodology and findings

### 2. For Engineers
- **Implement standards**: Help complete W3C DID, OAuth, MLS implementations
- **Fix bugs**: Address issues in Track 1 production code
- **Write tests**: Increase test coverage (no mocks!)
- **Improve performance**: Optimize existing implementations

### 3. For Users
- **Test features**: Use Track 1 features and report issues
- **Provide feedback**: Share your experience and suggestions
- **Participate in studies**: Opt into Track 2 experiments (with consent)
- **Report bugs**: File detailed issue reports

### 4. For Reviewers
- **Code review**: Review pull requests for quality and standards compliance
- **Documentation review**: Ensure clarity and accuracy
- **Security review**: Identify potential vulnerabilities
- **Compliance review**: Check EU AI Act and regulatory alignment

## Development Process

### Setting Up Your Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/mnemosyne.git
cd mnemosyne

# Run setup script
./scripts/setup.sh

# Start development environment
docker-compose up

# Run tests
docker-compose exec backend pytest
```

### Code Standards

#### Track 1 (Production) Requirements
- Use established standards (W3C, IETF, OpenID)
- Write real tests (no mocking)
- Include Model Cards for AI components
- Follow existing patterns in the codebase
- Ensure EU AI Act compliance

#### Track 2 (Experimental) Requirements
- Create hypothesis documentation in `docs/hypotheses/`
- Implement consent mechanisms
- Add "EXPERIMENTAL" warnings
- Include validation metrics
- Use the ExperimentalPlugin base class

### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run tests
   docker-compose exec backend pytest
   
   # Check linting
   docker-compose exec backend ruff check .
   
   # Type checking
   docker-compose exec backend mypy .
   ```

4. **Commit with clear messages**
   ```bash
   git add -A
   git commit -m "feat: Add W3C PROV integration for data lineage"
   ```

5. **Push and create PR**
   ```bash
   git push -u origin feature/your-feature-name
   # Then create a pull request on GitHub
   ```

## Pull Request Guidelines

### PR Requirements
- Clear description of changes
- Link to related issues
- Tests for new functionality
- Documentation updates
- No breaking changes to Track 1 without discussion

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (Track 1)
- [ ] New feature (Track 1)
- [ ] Experimental feature (Track 2)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] No mocking used

## Compliance
- [ ] EU AI Act considerations addressed
- [ ] Model Cards updated if applicable
- [ ] Privacy implications reviewed
```

## Hypothesis Validation Process

For Track 2 experimental features:

1. **Document hypothesis** in `docs/hypotheses/`
2. **Define success criteria** with measurable metrics
3. **Implement as plugin** using ExperimentalPlugin base
4. **Add consent flow** for data collection
5. **Collect metrics** during usage
6. **Analyze results** against criteria
7. **Publish findings** (positive or negative)
8. **Graduate to Track 1** only if validated

## Priority Areas

### 🚨 Urgent (Sprint 1C - Frontend)
- Connect React frontend to FastAPI backend
- Implement login and dashboard UI
- Wire up memory capture interface
- **This makes Mnemosyne usable!**

### High Priority
- Complete W3C PROV integration
- Implement MLS Protocol (Sprint 2A)
- Create transparency API endpoints
- Add WebAuthn/FIDO2 authentication

### Research Priorities
- Consent management system
- Behavioral stability tracking
- Identity compression validation
- Cross-cultural studies

## Communication

### Where to Get Help
- GitHub Issues: Bug reports and feature requests
- Discussions: General questions and ideas
- Documentation: Check `docs/` directory first

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive criticism
- Assume good intentions
- Help others learn and grow

## Recognition

Contributors will be recognized in:
- Git commit history
- CONTRIBUTORS.md file
- Release notes
- Research publications (for validation studies)

## Important Notes

### No Mocking Policy
We build real features or explicitly defer them. No fake implementations or placeholder code.

### Scientific Integrity
- Only proven features in Track 1
- Clear hypothesis documentation for Track 2
- Transparent about limitations
- Publish both positive and negative results

### Privacy First
- Never compromise on privacy
- Formal guarantees over promises
- Local-first architecture
- Consent for all data collection

## Questions?

If you have questions about contributing:
1. Check existing documentation in `docs/`
2. Look at similar code in the codebase
3. Review test files for examples
4. Open a GitHub issue for discussion

---

*"Building trustable AI through scientific validation and open standards."*

Thank you for helping us build a better future for cognitive sovereignty!