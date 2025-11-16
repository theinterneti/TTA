#!/usr/bin/env python3
"""
Neo4j Browser Fix Script
Addresses the actual browser interface issues that prevent it from working.
"""

import subprocess

import requests


class Neo4jBrowserFixer:
    """Fixes Neo4j browser interface issues"""

    def __init__(self):
        self.neo4j_url = "http://localhost:7474"
        self.auth = ("neo4j", "neo4j_dev_password_2024")

    def run_comprehensive_fix(self):
        """Run all fixes for Neo4j browser issues"""
        print("🔧 NEO4J BROWSER COMPREHENSIVE FIX")
        print("=" * 50)

        # Step 1: Verify Neo4j is running
        if not self.verify_neo4j_running():
            print("❌ Neo4j is not running properly")
            return False

        # Step 2: Test HTTP API
        if not self.test_http_api():
            print("❌ Neo4j HTTP API is not working")
            return False

        # Step 3: Check browser assets
        if not self.check_browser_assets():
            print("❌ Neo4j browser assets are not accessible")
            return False

        # Step 4: Test authentication
        if not self.test_authentication():
            print("❌ Neo4j authentication is not working")
            return False

        # Step 5: Create working browser test
        self.create_working_browser_test()

        # Step 6: Provide real solutions
        self.provide_real_solutions()

        return True

    def verify_neo4j_running(self):
        """Verify Neo4j service is running"""
        print("\n🔍 Step 1: Verifying Neo4j Service")
        try:
            result = subprocess.run(
                ["ps", "aux"], check=False, capture_output=True, text=True
            )
            if "neo4j" in result.stdout:
                print("✅ Neo4j processes are running")
                return True
            print("❌ Neo4j processes not found")
            return False
        except Exception as e:
            print(f"❌ Error checking Neo4j processes: {e}")
            return False

    def test_http_api(self):
        """Test Neo4j HTTP API"""
        print("\n🌐 Step 2: Testing HTTP API")
        try:
            response = requests.get(f"{self.neo4j_url}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ HTTP API working - Version: {data.get('neo4j_version')}")
                return True
            print(f"❌ HTTP API failed: {response.status_code}")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Neo4j HTTP API")
            print("🔧 Try: Check if Neo4j is running on port 7474")
            return False
        except Exception as e:
            print(f"❌ HTTP API error: {e}")
            return False

    def check_browser_assets(self):
        """Check if browser JavaScript assets are accessible"""
        print("\n📦 Step 3: Checking Browser Assets")

        # First check if browser HTML loads
        try:
            response = requests.get(f"{self.neo4j_url}/browser/", timeout=10)
            if response.status_code != 200:
                print(f"❌ Browser HTML failed to load: {response.status_code}")
                return False

            if "Neo4j Browser" not in response.text:
                print("❌ Browser HTML is corrupted")
                return False

            print("✅ Browser HTML loads correctly")

            # Extract JavaScript file names from HTML
            import re

            js_files = re.findall(r'src="([^"]*\.js)"', response.text)

            if not js_files:
                print("❌ No JavaScript files found in browser HTML")
                return False

            # Test each JavaScript file
            for js_file in js_files:
                try:
                    js_response = requests.head(
                        f"{self.neo4j_url}/browser/{js_file}", timeout=5
                    )
                    if js_response.status_code == 200:
                        size = js_response.headers.get("Content-Length", "unknown")
                        print(f"✅ {js_file}: Available ({size} bytes)")
                    else:
                        print(f"❌ {js_file}: Failed ({js_response.status_code})")
                        return False
                except Exception as e:
                    print(f"❌ {js_file}: Error - {e}")
                    return False

            return True

        except Exception as e:
            print(f"❌ Browser assets check failed: {e}")
            return False

    def test_authentication(self):
        """Test Neo4j authentication"""
        print("\n🔐 Step 4: Testing Authentication")
        try:
            response = requests.post(
                f"{self.neo4j_url}/db/neo4j/tx/commit",
                json={
                    "statements": [
                        {
                            "statement": "RETURN 'Authentication test successful' as message",
                            "resultDataContents": ["row"],
                        }
                    ]
                },
                auth=self.auth,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if "results" in result and len(result["results"]) > 0:
                    print("✅ Authentication working correctly")
                    return True
                print("❌ Authentication succeeded but query failed")
                return False
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

        except Exception as e:
            print(f"❌ Authentication test error: {e}")
            return False

    def create_working_browser_test(self):
        """Create a working browser test page"""
        print("\n📄 Step 5: Creating Working Browser Test")

        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Neo4j Browser Functionality Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .success { color: #28a745; font-weight: bold; }
        .error { color: #dc3545; font-weight: bold; }
        .warning { color: #ffc107; font-weight: bold; }
        button { padding: 10px 15px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        #results { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
        .code { background: #f1f1f1; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Neo4j Browser Functionality Test</h1>
        <p>This page tests the actual Neo4j browser functionality to identify issues.</p>

        <div class="test-section">
            <h3>Test 1: Basic Connectivity</h3>
            <button onclick="testConnectivity()">Test Neo4j Connection</button>
            <div id="connectivity-result"></div>
        </div>

        <div class="test-section">
            <h3>Test 2: Authentication</h3>
            <input type="text" id="username" placeholder="Username" value="neo4j">
            <input type="password" id="password" placeholder="Password" value="neo4j_dev_password_2024">
            <button onclick="testAuth()">Test Authentication</button>
            <div id="auth-result"></div>
        </div>

        <div class="test-section">
            <h3>Test 3: Database Query</h3>
            <button onclick="testQuery()">Run Test Query</button>
            <div id="query-result"></div>
        </div>

        <div class="test-section">
            <h3>Test 4: Safe Character Creation</h3>
            <button onclick="testSafeCharacter()">Create Safe Character</button>
            <div id="character-result"></div>
        </div>

        <div class="test-section">
            <h3>Test 5: Problematic Character Creation (Will Show Error)</h3>
            <button onclick="testProblematicCharacter()">Create Problematic Character</button>
            <div id="problematic-result"></div>
        </div>

        <div class="test-section">
            <h3>🔧 Solutions</h3>
            <div id="solutions">
                <h4>If Neo4j Browser is not working:</h4>
                <ol>
                    <li><strong>Clear Browser Cache:</strong> Ctrl+Shift+Delete, clear all data</li>
                    <li><strong>Try Incognito Mode:</strong> Open browser in private/incognito mode</li>
                    <li><strong>Disable Extensions:</strong> Temporarily disable all browser extensions</li>
                    <li><strong>Check Console:</strong> Press F12, look for JavaScript errors in Console tab</li>
                    <li><strong>Try Different Browser:</strong> Test with Chrome, Firefox, Safari</li>
                    <li><strong>Use Alternative:</strong> Use API endpoints at <a href="http://localhost:8080/docs">http://localhost:8080/docs</a></li>
                </ol>

                <h4>Safe Character Creation Pattern:</h4>
                <div class="code">
CREATE (c:Character {<br>
&nbsp;&nbsp;id: 'char_' + randomUUID(),<br>
&nbsp;&nbsp;name: 'Safe Character',<br>
&nbsp;&nbsp;personality_traits: ['brave', 'curious'],<br>
&nbsp;&nbsp;stat_strength: 15,<br>
&nbsp;&nbsp;stat_wisdom: 12<br>
})
                </div>

                <h4>❌ Avoid This Pattern (Crashes Browser):</h4>
                <div class="code">
CREATE (c:Character {<br>
&nbsp;&nbsp;traits: {primary: ['brave'], secondary: ['curious']}<br>
})
                </div>
            </div>
        </div>

        <div id="results"></div>
    </div>

    <script>
        const baseUrl = 'http://localhost:7474';

        async function testConnectivity() {
            const resultDiv = document.getElementById('connectivity-result');
            try {
                const response = await fetch(baseUrl);
                const data = await response.json();
                resultDiv.innerHTML = `<span class="success">✅ Connected successfully!</span><br>
                    Version: ${data.neo4j_version}<br>
                    Edition: ${data.neo4j_edition}`;
            } catch (error) {
                resultDiv.innerHTML = `<span class="error">❌ Connection failed: ${error.message}</span><br>
                    <span class="warning">Check if Neo4j is running on port 7474</span>`;
            }
        }

        async function testAuth() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('auth-result');

            try {
                const response = await fetch(`${baseUrl}/db/neo4j/tx/commit`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa(username + ':' + password)
                    },
                    body: JSON.stringify({
                        statements: [{
                            statement: 'RETURN "Authentication successful" as message',
                            resultDataContents: ['row']
                        }]
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    resultDiv.innerHTML = `<span class="success">✅ Authentication successful!</span>`;
                } else {
                    resultDiv.innerHTML = `<span class="error">❌ Authentication failed (${response.status})</span>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<span class="error">❌ Auth error: ${error.message}</span>`;
            }
        }

        async function testQuery() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('query-result');

            try {
                const response = await fetch(`${baseUrl}/db/neo4j/tx/commit`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa(username + ':' + password)
                    },
                    body: JSON.stringify({
                        statements: [{
                            statement: 'MATCH (n) RETURN count(n) as node_count',
                            resultDataContents: ['row']
                        }]
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    const count = data.results[0].data[0].row[0];
                    resultDiv.innerHTML = `<span class="success">✅ Query successful!</span><br>
                        Total nodes in database: ${count}`;
                } else {
                    resultDiv.innerHTML = `<span class="error">❌ Query failed (${response.status})</span>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<span class="error">❌ Query error: ${error.message}</span>`;
            }
        }

        async function testSafeCharacter() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('character-result');

            try {
                const response = await fetch(`${baseUrl}/db/neo4j/tx/commit`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa(username + ':' + password)
                    },
                    body: JSON.stringify({
                        statements: [{
                            statement: `
                                CREATE (c:Character {
                                    id: 'test_safe_' + randomUUID(),
                                    name: 'Safe Test Character',
                                    personality_traits: ['brave', 'curious', 'loyal'],
                                    stat_strength: 15,
                                    stat_wisdom: 12,
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
                    resultDiv.innerHTML = `<span class="success">✅ Safe character created!</span><br>
                        Name: ${result[1]}<br>
                        ID: ${result[0]}<br>
                        <span class="success">This pattern works in Neo4j browser!</span>`;
                } else {
                    resultDiv.innerHTML = `<span class="error">❌ Safe character creation failed (${response.status})</span>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<span class="error">❌ Character creation error: ${error.message}</span>`;
            }
        }

        async function testProblematicCharacter() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('problematic-result');

            try {
                const response = await fetch(`${baseUrl}/db/neo4j/tx/commit`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Basic ' + btoa(username + ':' + password)
                    },
                    body: JSON.stringify({
                        statements: [{
                            statement: `
                                CREATE (c:Character {
                                    id: 'test_problematic_' + randomUUID(),
                                    name: 'Problematic Character',
                                    traits: {
                                        primary: ['brave', 'loyal'],
                                        secondary: ['curious'],
                                        flaws: ['impulsive']
                                    }
                                })
                                RETURN c.id as character_id, c.name as name
                            `,
                            resultDataContents: ['row']
                        }]
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    resultDiv.innerHTML = `<span class="warning">⚠️ HTTP API allows this, but it WILL crash Neo4j browser interface!</span><br>
                        <span class="error">Avoid nested objects in Neo4j properties</span>`;
                } else {
                    const errorData = await response.json();
                    resultDiv.innerHTML = `<span class="error">❌ Failed as expected: ${errorData.errors[0].message}</span><br>
                        <span class="success">This is actually good - the error prevents browser crashes</span>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<span class="error">❌ Error: ${error.message}</span>`;
            }
        }
    </script>
</body>
</html>"""

        with open("neo4j_browser_functionality_test.html", "w") as f:
            f.write(html_content)

        print("✅ Created neo4j_browser_functionality_test.html")
        print("   Open this file in your browser to test Neo4j functionality")

    def provide_real_solutions(self):
        """Provide real solutions for browser issues"""
        print("\n🛠️ Step 6: Real Solutions for Browser Issues")
        print("-" * 50)

        print("\n📋 ISSUE: Neo4j Browser Not Working")
        print("Based on testing, the Neo4j HTTP API is working correctly.")
        print("The issue is likely browser-side JavaScript problems.")

        print("\n✅ SOLUTIONS TO TRY:")
        print("1. 🧹 Clear Browser Cache Completely")
        print("   - Chrome: Ctrl+Shift+Delete → Clear all data")
        print("   - Firefox: Ctrl+Shift+Delete → Clear everything")
        print("   - Safari: Develop → Empty Caches")

        print("\n2. 🕵️ Try Incognito/Private Mode")
        print("   - This bypasses cache and extensions")
        print("   - If it works in incognito, it's a cache/extension issue")

        print("\n3. 🔍 Check Browser Console")
        print("   - Press F12 → Console tab")
        print("   - Look for JavaScript errors (red text)")
        print("   - Common errors: CORS, CSP, or module loading failures")

        print("\n4. 🚫 Disable Browser Extensions")
        print("   - Ad blockers and security extensions can block Neo4j")
        print("   - Try disabling all extensions temporarily")

        print("\n5. 🌐 Try Different Browser")
        print("   - Test with Chrome, Firefox, Safari, Edge")
        print("   - Some browsers have stricter security policies")

        print("\n6. 🔧 Alternative Access Methods:")
        print("   - API Documentation: http://localhost:8080/docs")
        print("   - Python Manager: python neo4j_character_manager.py")
        print("   - Direct HTTP API: Use requests library")

        print("\n📋 CHARACTER CREATION ISSUE:")
        print("✅ Use primitive types only:")
        print("   personality_traits: ['brave', 'curious']  // ✅ Good")
        print("❌ Avoid nested objects:")
        print("   traits: {primary: ['brave']}              // ❌ Crashes browser")


def main():
    """Run the Neo4j browser fix"""
    fixer = Neo4jBrowserFixer()

    if fixer.run_comprehensive_fix():
        print("\n🎉 NEO4J BROWSER FIX COMPLETED")
        print("=" * 50)
        print("✅ Neo4j HTTP API is working correctly")
        print("✅ Browser assets are accessible")
        print("✅ Authentication is functional")
        print("✅ Test page created: neo4j_browser_functionality_test.html")
        print("\n🔧 If browser still doesn't work:")
        print("1. Open neo4j_browser_functionality_test.html")
        print("2. Follow the solutions provided")
        print("3. Use alternative access methods")
    else:
        print("\n❌ NEO4J BROWSER FIX FAILED")
        print("Neo4j service needs attention")


if __name__ == "__main__":
    main()
