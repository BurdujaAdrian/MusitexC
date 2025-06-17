import React, { useEffect, useRef } from 'react';
import abcjs from 'abcjs';
import 'abcjs/abcjs-audio.css';

interface ABCJSRendererProps {
  abcText: string;
}

const ABCJSRenderer: React.FC<ABCJSRendererProps> = ({ abcText }) => {
  const notationRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (notationRef.current) {
      abcjs.renderAbc(notationRef.current, abcText, {});
    }
  }, [abcText]);

  return <div ref={notationRef} />;
};

export default ABCJSRenderer;
