// Logseq: [[TTA.dev/Scripts/Send-slack-notification]]
#!/usr/bin/env node

/**
 * Send Slack Notification for E2E Test Results
 *
 * Sends detailed test results to Slack webhook with:
 * - Pass/fail summary
 * - Performance metrics
 * - Links to detailed reports
 * - Screenshots on failure
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL;
const TEST_RESULTS_PATH = process.env.TEST_RESULTS_PATH || 'test-results-staging/results.json';
const GITHUB_RUN_ID = process.env.GITHUB_RUN_ID;
const GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY;

/**
 * Read test results
 */
function readTestResults() {
  try {
    if (!fs.existsSync(TEST_RESULTS_PATH)) {
      console.warn(`⚠️ Test results file not found: ${TEST_RESULTS_PATH}`);
      return null;
    }

    const content = fs.readFileSync(TEST_RESULTS_PATH, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    console.error('❌ Failed to read test results:', error);
    return null;
  }
}

/**
 * Build Slack message
 */
function buildSlackMessage(results) {
  if (!results) {
    return {
      text: '⚠️ E2E Test Results - Unable to parse results',
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: '⚠️ *E2E Test Results*\nUnable to parse test results file',
          },
        },
      ],
    };
  }

  const stats = results.stats || {};
  const passed = stats.expected || 0;
  const failed = stats.unexpected || 0;
  const total = passed + failed;
  const passRate = total > 0 ? ((passed / total) * 100).toFixed(1) : 0;

  const statusEmoji = failed === 0 ? '✅' : '❌';
  const statusText = failed === 0 ? 'PASSED' : 'FAILED';
  const statusColor = failed === 0 ? '#36a64f' : '#ff0000';

  const reportUrl = `https://github.com/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}`;

  const blocks = [
    {
      type: 'header',
      text: {
        type: 'plain_text',
        text: `${statusEmoji} E2E Test Results - ${statusText}`,
        emoji: true,
      },
    },
    {
      type: 'section',
      fields: [
        {
          type: 'mrkdwn',
          text: `*Total Tests:*\n${total}`,
        },
        {
          type: 'mrkdwn',
          text: `*Passed:*\n${passed}`,
        },
        {
          type: 'mrkdwn',
          text: `*Failed:*\n${failed}`,
        },
        {
          type: 'mrkdwn',
          text: `*Pass Rate:*\n${passRate}%`,
        },
      ],
    },
  ];

  // Add performance metrics if available
  if (results.performance) {
    const perf = results.performance;
    blocks.push({
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Performance Metrics*\n• Page Load: ${perf.pageLoad?.toFixed(0)}ms\n• API Response: ${perf.apiResponse?.toFixed(0)}ms\n• AI Response: ${perf.aiResponse?.toFixed(0)}ms`,
      },
    });
  }

  // Add failed tests details
  if (failed > 0 && results.failures) {
    const failureText = results.failures
      .slice(0, 5)
      .map((f) => `• ${f.title}: ${f.error}`)
      .join('\n');

    blocks.push({
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Failed Tests*\n${failureText}${results.failures.length > 5 ? `\n... and ${results.failures.length - 5} more` : ''}`,
      },
    });
  }

  // Add action buttons
  blocks.push({
    type: 'actions',
    elements: [
      {
        type: 'button',
        text: {
          type: 'plain_text',
          text: 'View Full Report',
          emoji: true,
        },
        url: reportUrl,
        style: failed === 0 ? 'primary' : 'danger',
      },
    ],
  });

  return {
    text: `E2E Test Results - ${statusText}`,
    blocks,
    attachments: [
      {
        color: statusColor,
        footer: 'TTA E2E Testing',
        ts: Math.floor(Date.now() / 1000),
      },
    ],
  };
}

/**
 * Send message to Slack
 */
function sendSlackMessage(message) {
  return new Promise((resolve, reject) => {
    if (!SLACK_WEBHOOK_URL) {
      console.warn('⚠️ SLACK_WEBHOOK_URL not set, skipping notification');
      resolve();
      return;
    }

    const payload = JSON.stringify(message);

    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
      },
    };

    const req = https.request(SLACK_WEBHOOK_URL, options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log('✅ Slack notification sent successfully');
          resolve();
        } else {
          console.error(`❌ Slack notification failed: ${res.statusCode}`);
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    });

    req.on('error', (error) => {
      console.error('❌ Failed to send Slack notification:', error);
      reject(error);
    });

    req.write(payload);
    req.end();
  });
}

/**
 * Main execution
 */
async function main() {
  try {
    console.log('📤 Preparing Slack notification...');

    const results = readTestResults();
    const message = buildSlackMessage(results);

    await sendSlackMessage(message);

    console.log('✅ Slack notification completed');
    process.exit(0);
  } catch (error) {
    console.error('❌ Failed to send Slack notification:', error);
    process.exit(1);
  }
}

main();
