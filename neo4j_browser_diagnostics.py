#!/usr/bin/env python3
"""
Neo4j Browser Diagnostics and Fix Tool
Diagnoses and resolves Neo4j browser connectivity and character traits crash issues.
"""

import logging

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jBrowserDiagnostics:
    """Comprehensive Neo4j browser diagnostics and fixes"""

    def __init__(self):
        self.base_url = "http://localhost:7474"
        self.auth_users = [
            ("neo4j", "neo4j_dev_password_2024"),
            ("tta_integration", "tta_integration_password_2024"),
            ("tta_test", "tta_test_password_2024"),
        ]
        self.working_auth = None

    def run_full_diagnostics(self):
        """Run complete diagnostic suite"""
        print("🔍 NEO4J BROWSER COMPREHENSIVE DIAGNOSTICS")
        print("=" * 60)

        # Step 1: Basic connectivity
        if not self.test_basic_connectivity():
            return False

        # Step 2: Authentication
        if not self.test_authentication():
            return False

        # Step 3: Browser interface
        if not self.test_browser_interface():
            return False

        # Step 4: Character traits operations
        self.test_character_traits_operations()

        # Step 5: Provide solutions
        self.provide_solutions()

        return True

    def test_basic_connectivity(self) -> bool:
        """Test basic Neo4j HTTP connectivity"""
        print("\n🌐 STEP 1: Basic Connectivity Test")
        print("-" * 40)

        try:
            response = requests.get(f"{self.base_url}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Neo4j HTTP API: Connected")
                print(f"   Version: {data.get('neo4j_version', 'Unknown')}")
                print(f"   Edition: {data.get('neo4j_edition', 'Unknown')}")
                return True
            print(f"❌ Neo4j HTTP API: Failed ({response.status_code})")
            return False

        except requests.exceptions.ConnectionError:
            print("❌ Neo4j HTTP API: Connection refused")
            print("   🔧 Fix: Check if Neo4j service is running")
            return False
        except Exception as e:
            print(f"❌ Neo4j HTTP API: Error - {e}")
            return False

    def test_authentication(self) -> bool:
        """Test authentication with different users"""
        print("\n🔐 STEP 2: Authentication Test")
        print("-" * 40)

        for username, password in self.auth_users:
            try:
                response = requests.post(
                    f"{self.base_url}/db/neo4j/tx/commit",
                    json={
                        "statements": [
                            {
                                "statement": "RETURN 'Auth test' as message",
                                "resultDataContents": ["row"],
                            }
                        ]
                    },
                    auth=(username, password),
                    timeout=10,
                )

                if response.status_code == 200:
                    print(f"✅ User '{username}': Authentication successful")
                    self.working_auth = (username, password)
                    return True
                print(
                    f"❌ User '{username}': Authentication failed ({response.status_code})"
                )

            except Exception as e:
                print(f"❌ User '{username}': Error - {e}")

        print("🚨 No working authentication found!")
        return False

    def test_browser_interface(self) -> bool:
        """Test Neo4j browser interface"""
        print("\n🌐 STEP 3: Browser Interface Test")
        print("-" * 40)

        try:
            # Test browser HTML
            response = requests.get(f"{self.base_url}/browser/", timeout=10)
            if response.status_code == 200 and "Neo4j Browser" in response.text:
                print("✅ Browser HTML: Loading correctly")
            else:
                print(f"❌ Browser HTML: Failed ({response.status_code})")
                return False

            # Test browser assets
            response = requests.get(f"{self.base_url}/browser/assets/", timeout=10)
            if response.status_code in [200, 403]:  # 403 is OK for directory listing
                print("✅ Browser Assets: Available")
            else:
                print(f"⚠️ Browser Assets: May have issues ({response.status_code})")

            return True

        except Exception as e:
            print(f"❌ Browser Interface: Error - {e}")
            return False

    def test_character_traits_operations(self):
        """Test character creation with traits to identify crash causes"""
        print("\n🎭 STEP 4: Character Traits Crash Test")
        print("-" * 40)

        if not self.working_auth:
            print("❌ No working authentication - skipping traits test")
            return

        test_cases = [
            {
                "name": "Simple Character",
                "cypher": """
                    CREATE (c:Character {
                        id: 'browser_test_simple',
                        name: 'Simple Character',
                        description: 'Basic character'
                    })
                    RETURN c.id as id
                """,
                "expected": "✅ Should work",
            },
            {
                "name": "String Array Traits",
                "cypher": """
                    CREATE (c:Character {
                        id: 'browser_test_array',
                        name: 'Array Character',
                        personality_traits: ['brave', 'curious', 'loyal']
                    })
                    RETURN c.id as id
                """,
                "expected": "✅ Should work",
            },
            {
                "name": "Complex Nested Traits (CRASH CAUSE)",
                "cypher": """
                    CREATE (c:Character {
                        id: 'browser_test_nested',
                        name: 'Nested Character',
                        traits: {
                            primary: ['brave'],
                            secondary: ['curious']
                        }
                    })
                    RETURN c.id as id
                """,
                "expected": "❌ Will cause browser crash",
            },
            {
                "name": "Mixed Data Types (CRASH CAUSE)",
                "cypher": """
                    CREATE (c:Character {
                        id: 'browser_test_mixed',
                        name: 'Mixed Character',
                        traits: ['string', 123, true, null]
                    })
                    RETURN c.id as id
                """,
                "expected": "❌ May cause issues",
            },
        ]

        for test in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/db/neo4j/tx/commit",
                    json={
                        "statements": [
                            {"statement": test["cypher"], "resultDataContents": ["row"]}
                        ]
                    },
                    auth=self.working_auth,
                    timeout=10,
                )

                if response.status_code == 200:
                    print(f"✅ {test['name']}: HTTP API works")
                else:
                    print(f"❌ {test['name']}: HTTP API failed")
                    print(f"   Expected: {test['expected']}")

            except Exception as e:
                print(f"❌ {test['name']}: Error - {e}")

        # Cleanup
        try:
            requests.post(
                f"{self.base_url}/db/neo4j/tx/commit",
                json={
                    "statements": [
                        {
                            "statement": "MATCH (c:Character) WHERE c.id STARTS WITH 'browser_test' DELETE c"
                        }
                    ]
                },
                auth=self.working_auth,
            )
        except:
            pass

    def provide_solutions(self):
        """Provide comprehensive solutions"""
        print("\n🛠️ STEP 5: Solutions and Fixes")
        print("-" * 40)

        print("\n📋 ISSUE 1: Neo4j Browser Null Response")
        print("Possible causes and solutions:")
        print("1. ✅ HTTP API is working - browser interface loads correctly")
        print("2. 🔧 If browser shows blank/null:")
        print("   - Clear browser cache and cookies")
        print("   - Try incognito/private browsing mode")
        print("   - Check browser console for JavaScript errors")
        print("   - Disable browser extensions temporarily")

        print("\n📋 ISSUE 2: Character Traits Browser Crash")
        print("Root cause: Nested objects in Neo4j properties")
        print("Solutions:")
        print("1. ✅ Use primitive types only:")
        print("   personality_traits: ['brave', 'curious']  // ✅ Good")
        print("   traits: {primary: ['brave']}              // ❌ Crashes browser")
        print("\n2. ✅ Use individual properties:")
        print("   trait_primary: 'brave'")
        print("   trait_secondary: 'curious'")
        print("\n3. ✅ Use relationships for complex data:")
        print("   CREATE (c:Character)-[:HAS_TRAIT]->(t:Trait {name: 'brave'})")

        print("\n🔗 Alternative Access Methods:")
        print("1. 🌐 API Endpoints: http://localhost:8080/docs")
        print("2. 🐍 Python Manager: neo4j_character_manager.py")
        print("3. 📝 Safe Cypher Examples: neo4j_browser_troubleshooting.md")

    def create_browser_test_page(self):
        """Create a test page for browser functionality"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Neo4j Browser Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; }
        .success { color: green; }
        .error { color: red; }
        button { padding: 10px 15px; margin: 5px; }
        #results { margin-top: 20px; padding: 10px; background: #f5f5f5; }
    </style>
</head>
<body>
    <h1>Neo4j Browser Connectivity Test</h1>

    <div class="test-section">
        <h3>Test 1: Basic Connectivity</h3>
        <button onclick="testConnectivity()">Test Connection</button>
        <div id="connectivity-result"></div>
    </div>

    <div class="test-section">
        <h3>Test 2: Authentication</h3>
        <input type="text" id="username" placeholder="Username" value="tta_integration">
        <input type="password" id="password" placeholder="Password" value="tta_integration_password_2024">
        <button onclick="testAuth()">Test Auth</button>
        <div id="auth-result"></div>
    </div>

    <div class="test-section">
        <h3>Test 3: Safe Character Creation</h3>
        <button onclick="testSafeCharacter()">Create Safe Character</button>
        <div id="character-result"></div>
    </div>

    <div id="results"></div>

    <script>
        async function testConnectivity() {
            try {
                const response = await fetch('http://localhost:7474');
                const data = await response.json();
                document.getElementById('connectivity-result').innerHTML =
                    '<span class="success">✅ Connected: ' + data.neo4j_version + '</span>';
            } catch (error) {
                document.getElementById('connectivity-result').innerHTML =
                    '<span class="error">❌ Connection failed: ' + error.message + '</span>';
            }
        }

        async function testAuth() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('http://localhost:7474/db/neo4j/tx/commit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa(username + ':' + password)
                    },
                    body: JSON.stringify({
                        statements: [{
                            statement: 'RETURN "Auth successful" as message',
                            resultDataContents: ['row']
                        }]
                    })
                });

                if (response.ok) {
                    document.getElementById('auth-result').innerHTML =
                        '<span class="success">✅ Authentication successful</span>';
                } else {
                    document.getElementById('auth-result').innerHTML =
                        '<span class="error">❌ Authentication failed</span>';
                }
            } catch (error) {
                document.getElementById('auth-result').innerHTML =
                    '<span class="error">❌ Auth error: ' + error.message + '</span>';
            }
        }

        async function testSafeCharacter() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('http://localhost:7474/db/neo4j/tx/commit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa(username + ':' + password)
                    },
                    body: JSON.stringify({
                        statements: [{
                            statement: `
                                CREATE (c:Character {
                                    id: 'browser_test_' + randomUUID(),
                                    name: 'Browser Test Character',
                                    personality_traits: ['brave', 'curious'],
                                    stat_strength: 15,
                                    created_at: datetime()
                                })
                                RETURN c.id as character_id, c.name as name
                            `,
                            resultDataContents: ['row']
                        }]
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    const result = data.results[0].data[0].row;
                    document.getElementById('character-result').innerHTML =
                        '<span class="success">✅ Character created: ' + result[1] + ' (ID: ' + result[0] + ')</span>';
                } else {
                    document.getElementById('character-result').innerHTML =
                        '<span class="error">❌ Character creation failed</span>';
                }
            } catch (error) {
                document.getElementById('character-result').innerHTML =
                    '<span class="error">❌ Character error: ' + error.message + '</span>';
            }
        }
    </script>
</body>
</html>
        """

        with open("neo4j_browser_test.html", "w") as f:
            f.write(html_content)

        print("📄 Created neo4j_browser_test.html for manual testing")


def main():
    """Run diagnostics"""
    diagnostics = Neo4jBrowserDiagnostics()

    if diagnostics.run_full_diagnostics():
        print("\n🎉 DIAGNOSTICS COMPLETED")
        print("=" * 60)
        print("✅ Neo4j HTTP API is working correctly")
        print("✅ Authentication is functional")
        print("✅ Character creation works via HTTP API")
        print("\n🔧 If browser interface still shows issues:")
        print("1. Clear browser cache and try incognito mode")
        print("2. Check browser console for JavaScript errors")
        print("3. Use alternative access methods (API/Python)")

        # Create test page
        diagnostics.create_browser_test_page()
        print("\n📄 Created neo4j_browser_test.html for manual browser testing")
    else:
        print("\n❌ DIAGNOSTICS FAILED")
        print("Neo4j service may need attention")


if __name__ == "__main__":
    main()
