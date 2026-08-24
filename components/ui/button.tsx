import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex min-h-10 items-center justify-center gap-2 rounded-xl px-4 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2b6b52] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-[#183f31] text-white hover:bg-[#215541]',
        secondary: 'border border-[#d7ded8] bg-white text-[#263b31] hover:bg-[#f4f7f4]',
        success: 'bg-[#dcefe5] text-[#176343] hover:bg-[#cae8d8]',
        destructive: 'bg-[#fbe4e1] text-[#9e3029] hover:bg-[#f7d4cf]',
        ghost: 'text-[#4d5f56] hover:bg-[#eef2ee]',
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

