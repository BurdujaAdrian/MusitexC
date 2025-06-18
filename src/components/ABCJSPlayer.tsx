import React, { useEffect, useRef } from "react";
import abcjs from "abcjs";
import "abcjs/abcjs-audio.css";

interface ABCJSPlayerProps {
  abcText: string;
}

const ABCJSPlayer: React.FC<ABCJSPlayerProps> = ({ abcText }) => {
  const sheetRef = useRef<HTMLDivElement>(null);
  const synthControlRef = useRef<HTMLDivElement>(null);
  const synthController = useRef<any>(null);
  const visualObj = useRef<any>(null);

  useEffect(() => {
    if (sheetRef.current) {
      const [vObj] = abcjs.renderAbc(sheetRef.current, abcText);
      visualObj.current = vObj;
    }
    if (synthControlRef.current && visualObj.current) {
      const sc = new abcjs.synth.SynthController();
      sc.load(synthControlRef.current, null, {
        displayRestart: true,
        displayPlay: true,
        displayProgress: true,
        displayWarp: true,
      });
      const synth = new abcjs.synth.CreateSynth();
      synth.init({ visualObj: visualObj.current }).then(() => {
        sc.setTune(visualObj.current, false, {
          chordsOff: false,
          soundFontUrl: "https://paulrosen.github.io/midi-js-soundfonts/abcjs/",
        });
      });
      synthController.current = sc;
    }
    return () => {
      // Optionally clean up audio here
      if (synthController.current && synthController.current.pause) {
        synthController.current.pause();
      }
    };
  }, [abcText]);

  return (
    <div>
      <div ref={sheetRef} />
      <div ref={synthControlRef} style={{ margin: "1em 0" }} />
    </div>
  );
};

export default ABCJSPlayer;