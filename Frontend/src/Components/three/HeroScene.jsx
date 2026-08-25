import { Suspense, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshDistortMaterial, Sparkles } from '@react-three/drei';
import * as THREE from 'three';

const BRAND_COBALT = '#2457d6';
const BRAND_TEAL = '#087f75';

/** The signature 3D motif: a faceted core (precision/analysis) wrapped
 * in an orbiting wireframe shell (structure/evidence), drifting data
 * points around it (Sparkles). Reacts gently to the cursor. Built with
 * React Three Fiber rather than an embedded third-party scene, so it
 * stays on-brand, dependency-light, and fully self-contained. */
function AnalyticsCore({ reducedMotion }) {
  const coreRef = useRef();
  const shellRef = useRef();
  const groupRef = useRef();
  const pointer = useRef({ x: 0, y: 0 });

  useFrame((state, delta) => {
    if (!reducedMotion) {
      coreRef.current.rotation.y += delta * 0.25;
      coreRef.current.rotation.x += delta * 0.08;
      shellRef.current.rotation.y -= delta * 0.12;
      shellRef.current.rotation.z += delta * 0.05;
    }

    pointer.current.x = THREE.MathUtils.lerp(pointer.current.x, state.pointer.x, 0.04);
    pointer.current.y = THREE.MathUtils.lerp(pointer.current.y, state.pointer.y, 0.04);
    if (groupRef.current) {
      groupRef.current.rotation.y = pointer.current.x * 0.3;
      groupRef.current.rotation.x = -pointer.current.y * 0.2;
    }
  });

  return (
    <group ref={groupRef}>
      <Float speed={reducedMotion ? 0 : 1.4} rotationIntensity={reducedMotion ? 0 : 0.3} floatIntensity={reducedMotion ? 0 : 0.6}>
        <mesh ref={coreRef}>
          <icosahedronGeometry args={[1.15, 1]} />
          <MeshDistortMaterial
            color={BRAND_COBALT}
            metalness={0.15}
            roughness={0.35}
            distort={reducedMotion ? 0 : 0.22}
            speed={reducedMotion ? 0 : 1.6}
          />
        </mesh>
        <mesh ref={shellRef} scale={1.55}>
          <icosahedronGeometry args={[1.15, 1]} />
          <meshBasicMaterial color={BRAND_TEAL} wireframe transparent opacity={0.35} />
        </mesh>
      </Float>
      <Sparkles count={reducedMotion ? 0 : 40} scale={4.5} size={2.2} speed={0.25} color={BRAND_TEAL} opacity={0.6} />
    </group>
  );
}

function Lighting() {
  return (
    <>
      <ambientLight intensity={0.9} />
      <directionalLight position={[3, 4, 2]} intensity={1.6} color="#ffffff" />
      <pointLight position={[-3, -2, 2]} intensity={1.2} color={BRAND_TEAL} />
      <pointLight position={[2, -1, 3]} intensity={0.8} color="#8fb2ff" />
    </>
  );
}

/**
 * Landing-page 3D hero (frontendReadme's "wow factor" follow-up request).
 * Silently degrades to nothing if WebGL/rendering fails — the page's
 * text content never depends on this rendering successfully.
 */
export default function HeroScene({ className }) {
  const [failed, setFailed] = useState(false);
  const reducedMotion = useMemo(
    () => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    []
  );

  if (failed) return null;

  return (
    <div className={className} aria-hidden="true">
      <Canvas
        camera={{ position: [0, 0, 4.2], fov: 45 }}
        dpr={[1, 1.75]}
        gl={{ antialias: true, alpha: true }}
        onCreated={({ gl }) => gl.setClearColor(0x000000, 0)}
        onError={() => setFailed(true)}
      >
        <Suspense fallback={null}>
          <Lighting />
          <AnalyticsCore reducedMotion={reducedMotion} />
        </Suspense>
      </Canvas>
    </div>
  );
}
