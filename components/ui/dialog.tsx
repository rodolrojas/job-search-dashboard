'use client';

import * as DialogPrimitive from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

export const Dialog = DialogPrimitive.Root;
export const DialogTitle = DialogPrimitive.Title;
export const DialogDescription = DialogPrimitive.Description;

export function DialogContent({ className, children, ...props }: DialogPrimitive.DialogContentProps) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-[#10251c]/55 backdrop-blur-[2px] data-[state=open]:animate-[fade-in_180ms_ease-out]" />
      <DialogPrimitive.Content
        className={cn(
          'fixed left-1/2 top-1/2 z-50 max-h-[88vh] w-[min(760px,calc(100%-32px))] -translate-x-1/2 -translate-y-1/2 overflow-auto rounded-3xl border border-[#d6ddd7] bg-[#fbfcfa] p-6 shadow-[0_30px_100px_rgba(15,35,26,0.25)] dark:border-[#304139] dark:bg-[#111c16] dark:text-[#e8f0eb] dark:shadow-black/55 sm:p-8',
          className,
        )}
        {...props}
      >
        {children}
        <DialogPrimitive.Close className="absolute right-5 top-5 grid size-9 place-items-center rounded-full border border-[#dce2dc] bg-white text-[#536057] hover:bg-[#f0f3ef] dark:border-[#304139] dark:bg-[#18251e] dark:text-[#b5c4bc] dark:hover:bg-[#223129]" aria-label="Close dialog">
          <X size={16} />
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}
