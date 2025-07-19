import React from 'react';
import ThemeTest from '@/components/common/ThemeTest';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import Checkbox from '@/components/common/Checkbox';
import RadioGroup from '@/components/common/RadioGroup';
import { SkeletonCard } from '@/components/common/Skeleton';

const StorybookPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 text-foreground">EQDB Storybook / Style Guide</h1>
        <p className="text-muted-foreground mb-4">This is a static style guide for EQDB components. No API calls are made on this page. Navigation and search are disabled.</p>
      </div>
      <ThemeTest />
      <div className="my-8">
        <h2 className="text-2xl font-bold mb-4 text-foreground">Card Example</h2>
        <Card variant="default">
          <div className="p-4">This is a default card with the new border radius and padding.</div>
        </Card>
      </div>
      <div className="my-8">
        <h2 className="text-2xl font-bold mb-4 text-foreground">Button Examples</h2>
        <div className="flex gap-4 flex-wrap">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="danger">Danger</Button>
          <Button variant="warning">Warning</Button>
        </div>
      </div>
      <div className="my-8">
        <h2 className="text-2xl font-bold mb-4 text-foreground">Input, Checkbox, Radio</h2>
        <div className="flex flex-col gap-4 max-w-md">
          <Input label="Text Input" placeholder="Type here..." />
          <Checkbox label="Checkbox Example" />
          <RadioGroup label="Radio Example" options={['Option 1', 'Option 2']} value={'Option 1'} onChange={() => {}} />
        </div>
      </div>
      <div className="my-8">
        <h2 className="text-2xl font-bold mb-4 text-foreground">Skeleton Loading</h2>
        <SkeletonCard />
      </div>
    </div>
  );
};

export default StorybookPage; 