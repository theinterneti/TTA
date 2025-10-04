import type { Preview } from '@storybook/react';
import '../src/index.css';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    docs: {
      description: {
        component: 'TTA Therapeutic Platform Components - Interactive documentation and testing environment',
      },
    },
  },
  argTypes: {
    onChange: { action: 'changed' },
  },
};

export default preview;
