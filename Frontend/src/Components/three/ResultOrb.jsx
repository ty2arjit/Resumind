import { Suspense, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sparkles } from '@react-three/drei';
import { colorimetricColor } from '../../lib/colorimetric';

function Orb({ score, reducedMotion }) {
  const meshRef = useRef();
  const color = useMemo(() => colorimetricColor(score), [score]);

  useFrame((_, delta) => {
    if (!reducedMotion && meshRef.current) {
      meshRef.current.rotation.y += delta * 0.35;
      meshRef.current.rotation.x += delta * 0.12;
    }
  });

  return (
    <group>
      <mesh ref={meshRef}>
        <dodecahedronGeometry args={[1, 0]} />
        <meshStandardMaterial color={color} metalness={0.1} roughness={0.4} />
      </mesh>
      <mesh scale={1.35}>
        <dodecahedronGeometry args={[1, 0]} />
        <meshBasicMaterial color={color} wireframe transparent opacity={0.25} />
      </mesh>
      <Sparkles count={reducedMotion ? 0 : 24} scale={3.2} size={2} speed={0.2} color={color} opacity={0.55} />
    </group>
  );
}

/**
 * A compact, score-tinted 3D accent for the result page — sits behind
 * the ColorimetricMeter. Same self-contained, dependency-light approach
 * as the landing page's HeroScene; silently disappears if rendering
 * fails so the score/text content never depends on it.
 */
export default function ResultOrb({ score, className }) {
  const [failed, setFailed] = useState(false);
  const reducedMotion = useMemo(
    () => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    []
  );

  if (failed) return null;

  return (
    <div className={className} aria-hidden="true">
      <Canvas
        camera={{ position: [0, 0, 3.2], fov: 45 }}
        dpr={[1, 1.75]}
        gl={{ antialias: true, alpha: true }}
        onCreated={({ gl }) => gl.setClearColor(0x000000, 0)}
        onError={() => setFailed(true)}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.9} />
          <directionalLight position={[3, 4, 2]} intensity={1.4} />
          <Orb score={score} reducedMotion={reducedMotion} />
        </Suspense>
      </Canvas>
    </div>
  );
}
