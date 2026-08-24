import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex min-h-10 items-center justify-center gap-2 rounded-xl px-4 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2b6b52] focus-visible:ring-offset-2 dark:focus-visible:ring-[#77b997] dark:focus-visible:ring-offset-[#0d1511] disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-[#183f31] text-white hover:bg-[#215541]',
        secondary: 'border border-[#d7ded8] bg-white text-[#263b31] hover:bg-[#f4f7f4] dark:border-[#304139] dark:bg-[#15211b] dark:text-[#c7d5ce] dark:hover:bg-[#203029]',
        success: 'bg-[#dcefe5] text-[#176343] hover:bg-[#cae8d8] dark:bg-[#193d2d] dark:text-[#8bd4af] dark:hover:bg-[#214d39]',
        destructive: 'bg-[#fbe4e1] text-[#9e3029] hover:bg-[#f7d4cf] dark:bg-[#49231f] dark:text-[#efa49e] dark:hover:bg-[#5b2c27]',
        ghost: 'text-[#4d5f56] hover:bg-[#eef2ee] dark:text-[#aebfb6] dark:hover:bg-[#223129]',
      },
      size: {
        default: 'h-10',
        sm: 'h-9 min-h-9 rounded-lg px-3 text-xs',
        icon: 'size-10 min-h-10 p-0',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  ),
);
Button.displayName = 'Button';
