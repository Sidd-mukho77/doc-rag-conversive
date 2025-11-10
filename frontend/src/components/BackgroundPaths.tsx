"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface BackgroundPathsProps {
  children?: ReactNode;
  className?: string;
}

export function BackgroundPaths({ children, className = "" }: BackgroundPathsProps) {
  const paths = [
    "M10 80 Q 52.5 10, 95 80 T 180 80",
    "M20 120 Q 80 60, 140 120 T 260 120",
    "M30 40 Q 90 100, 150 40 T 270 40",
    "M40 160 Q 100 100, 160 160 T 280 160",
    "M50 200 Q 110 140, 170 200 T 290 200",
    "M60 240 Q 120 180, 180 240 T 300 240",
    "M70 280 Q 130 220, 190 280 T 310 280",
    "M80 320 Q 140 260, 200 320 T 320 320",
    "M90 360 Q 150 300, 210 360 T 330 360",
    "M100 400 Q 160 340, 220 400 T 340 400",
    "M110 440 Q 170 380, 230 440 T 350 440",
    "M120 480 Q 180 420, 240 480 T 360 480",
    "M130 520 Q 190 460, 250 520 T 370 520",
    "M140 560 Q 200 500, 260 560 T 380 560",
    "M150 600 Q 210 540, 270 600 T 390 600",
    "M160 640 Q 220 580, 280 640 T 400 640",
    "M170 680 Q 230 620, 290 680 T 410 680",
    "M180 720 Q 240 660, 300 720 T 420 720",
    "M190 60 Q 250 0, 310 60 T 430 60",
    "M200 100 Q 260 40, 320 100 T 440 100",
    "M210 140 Q 270 80, 330 140 T 450 140",
    "M220 180 Q 280 120, 340 180 T 460 180",
    "M230 220 Q 290 160, 350 220 T 470 220",
    "M240 260 Q 300 200, 360 260 T 480 260",
    "M250 300 Q 310 240, 370 300 T 490 300",
    "M260 340 Q 320 280, 380 340 T 500 340",
    "M270 380 Q 330 320, 390 380 T 510 380",
    "M280 420 Q 340 360, 400 420 T 520 420",
    "M290 460 Q 350 400, 410 460 T 530 460",
    "M300 500 Q 360 440, 420 500 T 540 500",
    "M310 540 Q 370 480, 430 540 T 550 540",
    "M320 580 Q 380 520, 440 580 T 560 580",
    "M330 620 Q 390 560, 450 620 T 570 620",
    "M340 660 Q 400 600, 460 660 T 580 660",
    "M350 700 Q 410 640, 470 700 T 590 700",
    "M360 740 Q 420 680, 480 740 T 600 740",
  ];

  return (
    <>
      <div className={`fixed inset-0 -z-10 overflow-hidden bg-neutral-950 ${className}`}>
        <svg
          className="absolute inset-0 h-full w-full"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="path-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="rgb(168, 85, 247)" stopOpacity="0.4" />
              <stop offset="100%" stopColor="rgb(236, 72, 153)" stopOpacity="0.4" />
            </linearGradient>
          </defs>
          {paths.map((path, index) => (
            <motion.path
              key={index}
              d={path}
              stroke="url(#path-gradient)"
              strokeWidth="2"
              fill="none"
              initial={{ opacity: 0.1, pathLength: 0 }}
              animate={{
                opacity: [0.1, 0.6, 0.1],
                pathLength: [0, 1, 0],
                y: [-20, 20, -20],
              }}
              transition={{
                duration: 8 + index * 0.5,
                repeat: Infinity,
                ease: "easeInOut",
                delay: index * 0.1,
              }}
            />
          ))}
        </svg>
      </div>
      {children}
    </>
  );
}
