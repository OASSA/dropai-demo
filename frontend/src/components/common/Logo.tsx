interface LogoIconProps {
  size?: number;
  className?: string;
}

/** SVG recreation of the DropAI diamond logo icon */
export function LogoIcon({ size = 40, className }: LogoIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Red rounded diamond background */}
      <rect
        x="13" y="13" width="74" height="74" rx="17"
        fill="#CC3318"
        transform="rotate(45 50 50)"
      />

      {/* Vertical stem of D */}
      <line x1="34" y1="31" x2="34" y2="69" stroke="white" strokeWidth="5" strokeLinecap="round" />

      {/* Curved right side of D */}
      <path
        d="M34 31 Q72 31 72 50 Q72 69 34 69"
        stroke="white" strokeWidth="4.5" fill="none" strokeLinecap="round" strokeLinejoin="round"
      />

      {/* Circuit nodes — left of D stem */}
      <circle cx="26" cy="40" r="4" fill="white" />
      <circle cx="26" cy="50" r="4" fill="white" />
      <circle cx="26" cy="60" r="4" fill="white" />

      {/* Connector lines from nodes to stem */}
      <line x1="30" y1="40" x2="34" y2="40" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="30" y1="50" x2="34" y2="50" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="30" y1="60" x2="34" y2="60" stroke="white" strokeWidth="2.5" strokeLinecap="round" />

      {/* Package / box icon inside D */}
      <rect x="48" y="42" width="18" height="16" rx="2.5" fill="white" />
      <line x1="48" y1="48.5" x2="66" y2="48.5" stroke="#CC3318" strokeWidth="1.8" />
      <line x1="57" y1="42" x2="57" y2="58" stroke="#CC3318" strokeWidth="1.8" />
    </svg>
  );
}

interface LogoFullProps {
  iconSize?: number;
  textSize?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

const textSizeMap = {
  sm: "text-base",
  md: "text-xl",
  lg: "text-2xl",
  xl: "text-3xl",
};

/** Full logo: icon + "Drop AI" wordmark */
export function LogoFull({ iconSize = 40, textSize = "md", className }: LogoFullProps) {
  return (
    <div className={`flex items-center gap-2.5 ${className ?? ""}`}>
      <LogoIcon size={iconSize} />
      <span className={`font-extrabold tracking-tight text-[#CC3318] ${textSizeMap[textSize]}`}>
        Drop <span className="text-gray-900">AI</span>
      </span>
    </div>
  );
}

/** White version for dark backgrounds */
export function LogoFullWhite({ iconSize = 36, textSize = "md", className }: LogoFullProps) {
  return (
    <div className={`flex items-center gap-2.5 ${className ?? ""}`}>
      <LogoIcon size={iconSize} />
      <span className={`font-extrabold tracking-tight text-white ${textSizeMap[textSize]}`}>
        Drop AI
      </span>
    </div>
  );
}
