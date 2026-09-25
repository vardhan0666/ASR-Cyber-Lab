import { useEffect, useRef } from "react";
import * as THREE from "three";

interface LegParts {
  upper: THREE.Mesh;
  lower: THREE.Mesh;
  joint: THREE.Mesh;
  tip: THREE.Mesh;
  baseAngle: number;
  phase: number;
}

function placeCylinder(
  mesh: THREE.Mesh,
  from: THREE.Vector3,
  to: THREE.Vector3,
) {
  const direction = new THREE.Vector3().subVectors(to, from);
  const length = direction.length();

  if (length < 0.0001) {
    return;
  }

  const midpoint = new THREE.Vector3()
    .addVectors(from, to)
    .multiplyScalar(0.5);

  mesh.position.copy(midpoint);
  mesh.scale.set(1, length, 1);

  mesh.quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction.normalize(),
  );
}

export default function CyberScene() {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const mount = mountRef.current;

    if (!mount) {
      return;
    }

    let destroyed = false;

    const scene = new THREE.Scene();

    scene.fog = new THREE.FogExp2(0x020409, 0.035);

    const camera = new THREE.PerspectiveCamera(
      48,
      window.innerWidth / window.innerHeight,
      0.1,
      120,
    );

    camera.position.set(0, 0, 28);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });

    renderer.setPixelRatio(
      Math.min(window.devicePixelRatio, 1.6),
    );

    renderer.setSize(
      window.innerWidth,
      window.innerHeight,
    );

    renderer.domElement.style.position = "fixed";
    renderer.domElement.style.inset = "0";
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.pointerEvents = "none";
    renderer.domElement.style.zIndex = "0";

    mount.appendChild(renderer.domElement);

    /*
     * ---------------------------------------------------------
     * Background particle field
     * ---------------------------------------------------------
     */

    const particleCount = 240;

    const particlePositions = new Float32Array(
      particleCount * 3,
    );

    const particleBase = new Float32Array(
      particleCount * 3,
    );

    const particlePhase = new Float32Array(
      particleCount,
    );

    for (let index = 0; index < particleCount; index += 1) {
      const offset = index * 3;

      const x = (Math.random() - 0.5) * 42;
      const y = (Math.random() - 0.5) * 26;
      const z = (Math.random() - 0.5) * 22;

      particlePositions[offset] = x;
      particlePositions[offset + 1] = y;
      particlePositions[offset + 2] = z;

      particleBase[offset] = x;
      particleBase[offset + 1] = y;
      particleBase[offset + 2] = z;

      particlePhase[index] =
        Math.random() * Math.PI * 2;
    }

    const particleGeometry =
      new THREE.BufferGeometry();

    particleGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(
        particlePositions,
        3,
      ),
    );

    const particleMaterial =
      new THREE.PointsMaterial({
        color: 0x38bdf8,
        size: 0.055,
        transparent: true,
        opacity: 0.48,
        depthWrite: false,
      });

    const particles = new THREE.Points(
      particleGeometry,
      particleMaterial,
    );

    scene.add(particles);

    /*
     * ---------------------------------------------------------
     * Network graph
     * ---------------------------------------------------------
     */

    const nodeCount = 42;
    const connectionCount = 68;

    const nodes: THREE.Vector3[] = [];

    for (let index = 0; index < nodeCount; index += 1) {
      nodes.push(
        new THREE.Vector3(
          (Math.random() - 0.5) * 32,
          (Math.random() - 0.5) * 19,
          (Math.random() - 0.5) * 11,
        ),
      );
    }

    const connectionPairs: [number, number][] = [];

    for (
      let index = 0;
      index < connectionCount;
      index += 1
    ) {
      let a = Math.floor(
        Math.random() * nodeCount,
      );

      let b = Math.floor(
        Math.random() * nodeCount,
      );

      if (a === b) {
        b = (b + 1) % nodeCount;
      }

      connectionPairs.push([a, b]);
    }

    const linePositions =
      new Float32Array(
        connectionCount * 2 * 3,
      );

    const networkGeometry =
      new THREE.BufferGeometry();

    networkGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(
        linePositions,
        3,
      ),
    );

    const networkMaterial =
      new THREE.LineBasicMaterial({
        color: 0x0e7490,
        transparent: true,
        opacity: 0.22,
        depthWrite: false,
      });

    const networkLines =
      new THREE.LineSegments(
        networkGeometry,
        networkMaterial,
      );

    scene.add(networkLines);

    /*
     * ---------------------------------------------------------
     * HUD rings
     * ---------------------------------------------------------
     */

    const ringGroup =
      new THREE.Group();

    scene.add(ringGroup);

    const ringConfigurations = [
      {
        radius: 5.8,
        tube: 0.012,
        rotationX: 0.8,
        rotationY: 0.2,
      },
      {
        radius: 8.6,
        tube: 0.009,
        rotationX: 1.3,
        rotationY: -0.5,
      },
      {
        radius: 11.2,
        tube: 0.007,
        rotationX: 0.35,
        rotationY: 1.0,
      },
    ];

    ringConfigurations.forEach(
      (configuration) => {
        const ring =
          new THREE.Mesh(
            new THREE.TorusGeometry(
              configuration.radius,
              configuration.tube,
              8,
              160,
            ),
            new THREE.MeshBasicMaterial({
              color: 0x38bdf8,
              transparent: true,
              opacity: 0.11,
              wireframe: true,
              depthWrite: false,
            }),
          );

        ring.rotation.x =
          configuration.rotationX;

        ring.rotation.y =
          configuration.rotationY;

        ringGroup.add(ring);
      },
    );

    /*
     * ---------------------------------------------------------
     * Rotating arcs
     * ---------------------------------------------------------
     */

    const arcGroup =
      new THREE.Group();

    scene.add(arcGroup);

    for (let index = 0; index < 4; index += 1) {
      const arc =
        new THREE.Mesh(
          new THREE.TorusGeometry(
            13 + index * 1.8,
            0.012,
            6,
            100,
            Math.PI * 0.78,
          ),
          new THREE.MeshBasicMaterial({
            color:
              index % 2 === 0
                ? 0x67e8f9
                : 0x8b5cf6,
            transparent: true,
            opacity: 0.14,
            depthWrite: false,
          }),
        );

      arc.rotation.x =
        index * 0.35;

      arc.rotation.y =
        index * 0.22;

      arc.rotation.z =
        index * 0.8;

      arcGroup.add(arc);
    }

    /*
     * ---------------------------------------------------------
     * 3D creature cursor
     * ---------------------------------------------------------
     */

    const creature =
      new THREE.Group();

    creature.position.z = 1.4;

    scene.add(creature);

    const coreMaterial =
      new THREE.MeshBasicMaterial({
        color: 0x67e8f9,
      });

    const darkMaterial =
      new THREE.MeshBasicMaterial({
        color: 0x07131c,
      });

    const violetMaterial =
      new THREE.MeshBasicMaterial({
        color: 0x8b5cf6,
      });

    const body =
      new THREE.Mesh(
        new THREE.IcosahedronGeometry(
          0.72,
          1,
        ),
        darkMaterial,
      );

    creature.add(body);

    const bodyGlow =
      new THREE.Mesh(
        new THREE.IcosahedronGeometry(
          0.79,
          1,
        ),
        new THREE.MeshBasicMaterial({
          color: 0x38bdf8,
          wireframe: true,
          transparent: true,
          opacity: 0.42,
        }),
      );

    creature.add(bodyGlow);

    const core =
      new THREE.Mesh(
        new THREE.SphereGeometry(
          0.26,
          16,
          16,
        ),
        coreMaterial,
      );

    creature.add(core);

    const coreRing =
      new THREE.Mesh(
        new THREE.TorusGeometry(
          0.42,
          0.025,
          8,
          48,
        ),
        new THREE.MeshBasicMaterial({
          color: 0x67e8f9,
          transparent: true,
          opacity: 0.72,
        }),
      );

    coreRing.rotation.x =
      Math.PI / 2;

    creature.add(coreRing);

    /*
     * Eyes
     */

    const eyeMaterial =
      new THREE.MeshBasicMaterial({
        color: 0xffffff,
      });

    const eyeLeft =
      new THREE.Mesh(
        new THREE.SphereGeometry(
          0.07,
          10,
          10,
        ),
        eyeMaterial,
      );

    const eyeRight =
      eyeLeft.clone();

    eyeLeft.position.set(
      -0.21,
      0.16,
      0.61,
    );

    eyeRight.position.set(
      0.21,
      0.16,
      0.61,
    );

    creature.add(
      eyeLeft,
      eyeRight,
    );

    /*
     * ---------------------------------------------------------
     * Spider legs
     * ---------------------------------------------------------
     */

    const legGeometry =
      new THREE.CylinderGeometry(
        0.045,
        0.085,
        1,
        6,
      );

    const jointGeometry =
      new THREE.SphereGeometry(
        0.095,
        8,
        8,
      );

    const tipGeometry =
      new THREE.SphereGeometry(
        0.055,
        7,
        7,
      );

    const legMaterial =
      new THREE.MeshBasicMaterial({
        color: 0x38bdf8,
      });

    const legMaterialAlt =
      new THREE.MeshBasicMaterial({
        color: 0x8b5cf6,
      });

    const legs: LegParts[] = [];

    for (let index = 0; index < 8; index += 1) {
      const baseAngle =
        (index / 8) *
        Math.PI *
        2;

      const upper =
        new THREE.Mesh(
          legGeometry.clone(),
          index % 2 === 0
            ? legMaterial
            : legMaterialAlt,
        );

      const lower =
        new THREE.Mesh(
          legGeometry.clone(),
          index % 2 === 0
            ? legMaterial
            : legMaterialAlt,
        );

      const joint =
        new THREE.Mesh(
          jointGeometry.clone(),
          violetMaterial,
        );

      const tip =
        new THREE.Mesh(
          tipGeometry.clone(),
          coreMaterial,
        );

      creature.add(
        upper,
        lower,
        joint,
        tip,
      );

      /*
       * Important:
       *
       * The 8 legs are deliberately phased into
       * alternating gait groups.
       *
       * Group A:
       * 0, 2, 4, 6
       *
       * Group B:
       * 1, 3, 5, 7
       */

      const gaitGroup =
        index % 2;

      legs.push({
        upper,
        lower,
        joint,
        tip,
        baseAngle,
        phase:
          gaitGroup === 0
            ? 0
            : Math.PI,
      });
    }

    /*
     * ---------------------------------------------------------
     * Cursor input
     * ---------------------------------------------------------
     */

    const pointer =
      new THREE.Vector2();

    const pointerTarget =
      new THREE.Vector3(
        0,
        0,
        1.4,
      );

    const pointerCurrent =
      new THREE.Vector3(
        0,
        0,
        1.4,
      );

    const previousPointer =
      new THREE.Vector3(
        0,
        0,
        1.4,
      );

    const velocity =
      new THREE.Vector3();

    const movementDirection =
      new THREE.Vector3(
        1,
        0,
        0,
      );

    const raycaster =
      new THREE.Raycaster();

    const pointerPlane =
      new THREE.Plane(
        new THREE.Vector3(
          0,
          0,
          1,
        ),
        -1.4,
      );

    let interactiveHover = false;
    let pulseTime = -10;

    const handlePointerMove = (
      event: PointerEvent,
    ) => {
      pointer.x =
        (event.clientX /
          window.innerWidth) *
          2 -
        1;

      pointer.y =
        -(event.clientY /
          window.innerHeight) *
          2 +
        1;

      const target =
        event.target as HTMLElement | null;

      interactiveHover =
        Boolean(
          target?.closest(
            "button, a, input, select, textarea, [role='button'], [data-cursor='interactive']",
          ),
        );
    };

    const handlePointerDown = () => {
      pulseTime =
        performance.now() / 1000;
    };

    window.addEventListener(
      "pointermove",
      handlePointerMove,
    );

    window.addEventListener(
      "pointerdown",
      handlePointerDown,
    );

    /*
     * ---------------------------------------------------------
     * Click pulse
     * ---------------------------------------------------------
     */

    const pulse =
      new THREE.Mesh(
        new THREE.RingGeometry(
          0.2,
          0.28,
          32,
        ),
        new THREE.MeshBasicMaterial({
          color: 0x67e8f9,
          transparent: true,
          opacity: 0,
          side: THREE.DoubleSide,
          depthWrite: false,
        }),
      );

    pulse.position.z = 0.8;

    creature.add(pulse);

    /*
     * ---------------------------------------------------------
     * Animation
     * ---------------------------------------------------------
     */

    const clock =
      new THREE.Clock();

    const animate = () => {
      if (destroyed) {
        return;
      }

      const elapsed =
        clock.getElapsedTime();

      /*
       * -------------------------------------------------------
       * Particle animation
       * -------------------------------------------------------
       */

      const particleAttribute =
        particleGeometry.getAttribute(
          "position",
        ) as THREE.BufferAttribute;

      for (
        let index = 0;
        index < particleCount;
        index += 1
      ) {
        const offset =
          index * 3;

        const phase =
          particlePhase[index];

        particleAttribute.array[
          offset
        ] =
          particleBase[offset] +
          Math.sin(
            elapsed * 0.16 +
              phase,
          ) *
            0.16;

        particleAttribute.array[
          offset + 1
        ] =
          particleBase[offset + 1] +
          Math.cos(
            elapsed * 0.13 +
              phase,
          ) *
            0.14;

        particleAttribute.array[
          offset + 2
        ] =
          particleBase[offset + 2] +
          Math.sin(
            elapsed * 0.1 +
              phase,
          ) *
            0.12;
      }

      particleAttribute.needsUpdate =
        true;

      /*
       * -------------------------------------------------------
       * Network animation
       * -------------------------------------------------------
       */

      for (
        let index = 0;
        index < nodeCount;
        index += 1
      ) {
        const node =
          nodes[index];

        node.x +=
          Math.sin(
            elapsed * 0.08 +
              index,
          ) *
          0.0015;

        node.y +=
          Math.cos(
            elapsed * 0.07 +
              index * 0.7,
          ) *
          0.0015;
      }

      const lineAttribute =
        networkGeometry.getAttribute(
          "position",
        ) as THREE.BufferAttribute;

      connectionPairs.forEach(
        ([a, b], index) => {
          const first =
            nodes[a];

          const second =
            nodes[b];

          const offset =
            index * 6;

          lineAttribute.array[
            offset
          ] = first.x;

          lineAttribute.array[
            offset + 1
          ] = first.y;

          lineAttribute.array[
            offset + 2
          ] = first.z;

          lineAttribute.array[
            offset + 3
          ] = second.x;

          lineAttribute.array[
            offset + 4
          ] = second.y;

          lineAttribute.array[
            offset + 5
          ] = second.z;
        },
      );

      lineAttribute.needsUpdate =
        true;

      /*
       * -------------------------------------------------------
       * Ambient world animation
       * -------------------------------------------------------
       */

      particles.rotation.y =
        elapsed * 0.006;

      networkLines.rotation.y =
        elapsed * 0.008;

      ringGroup.rotation.z =
        elapsed * 0.018;

      ringGroup.rotation.y =
        elapsed * 0.009;

      arcGroup.rotation.z =
        -elapsed * 0.014;

      arcGroup.rotation.x =
        Math.sin(
          elapsed * 0.12,
        ) *
        0.04;

      /*
       * -------------------------------------------------------
       * Convert mouse position to world space
       * -------------------------------------------------------
       */

      raycaster.setFromCamera(
        pointer,
        camera,
      );

      raycaster.ray.intersectPlane(
        pointerPlane,
        pointerTarget,
      );

      /*
       * -------------------------------------------------------
       * Smooth creature movement
       * -------------------------------------------------------
       */

      pointerCurrent.lerp(
        pointerTarget,
        0.14,
      );

      velocity
        .subVectors(
          pointerCurrent,
          previousPointer,
        )
        .multiplyScalar(60);

      previousPointer.copy(
        pointerCurrent,
      );

      const velocityMagnitude =
        velocity.length();

      const movementAmount =
        THREE.MathUtils.clamp(
          velocityMagnitude / 2.2,
          0,
          1,
        );

      if (
        velocityMagnitude >
        0.015
      ) {
        movementDirection
          .copy(velocity)
          .normalize();
      }

      creature.position.x =
        pointerCurrent.x;

      creature.position.y =
        pointerCurrent.y;

      /*
       * -------------------------------------------------------
       * Body reaction
       * -------------------------------------------------------
       */

      creature.rotation.z =
        Math.sin(
          elapsed * 2.4,
        ) *
        0.055;

      creature.rotation.x =
        pointer.y * 0.08;

      creature.rotation.y =
        pointer.x * -0.08;

      const hoverScale =
        interactiveHover
          ? 1.14
          : 1;

      const breathing =
        1 +
        Math.sin(
          elapsed * 2.8,
        ) *
          0.035;

      creature.scale.setScalar(
        breathing *
          hoverScale,
      );

      bodyGlow.rotation.x =
        elapsed * 0.6;

      bodyGlow.rotation.y =
        elapsed * 0.9;

      coreRing.rotation.z =
        elapsed * 1.7;

      core.scale.setScalar(
        1 +
          Math.sin(
            elapsed * 4,
          ) *
          0.13,
      );

      /*
       * -------------------------------------------------------
       * REAL SPIDER GAIT
       * -------------------------------------------------------
       *
       * Every leg now performs:
       *
       * 1. backward planted phase
       * 2. lift
       * 3. forward swing
       * 4. plant
       *
       * Opposite legs are 180° out of phase.
       */

      const stepSpeed =
        3.0 +
        movementAmount * 7.0;

      const idleLift =
        0.05;

      legs.forEach(
        (leg, index) => {
          /*
           * Each leg has its own continuous phase.
           */

          const cycle =
            elapsed *
              stepSpeed +
            leg.phase +
            index * 0.06;

          /*
           * 0 → 1 → 0 lifting envelope.
           */

          const liftWave =
            Math.max(
              0,
              Math.sin(cycle),
            );

          const lift =
            THREE.MathUtils.lerp(
              idleLift,
              0.58,
              Math.pow(
                liftWave,
                1.35,
              ),
            );

          /*
           * Forward/back swing.
           */

          const swing =
            Math.cos(cycle);

          /*
           * Spider geometry.
           */

          const radial =
            new THREE.Vector3(
              Math.cos(
                leg.baseAngle,
              ),
              Math.sin(
                leg.baseAngle,
              ) * 0.82,
              0,
            ).normalize();

          const tangent =
            new THREE.Vector3(
              -Math.sin(
                leg.baseAngle,
              ),
              Math.cos(
                leg.baseAngle,
              ) * 0.82,
              0,
            ).normalize();

          /*
           * Base point.
           */

          const base =
            radial
              .clone()
              .multiplyScalar(0.50);

          base.z = 0.08;

          /*
           * Elbow:
           * pushed outward and raised while walking.
           */

          const elbow =
            radial
              .clone()
              .multiplyScalar(
                1.22,
              );

          elbow.add(
            tangent
              .clone()
              .multiplyScalar(
                0.16 *
                  (index % 2 === 0
                    ? 1
                    : -1),
              ),
          );

          elbow.add(
            movementDirection
              .clone()
              .multiplyScalar(
                0.16 *
                  movementAmount,
              ),
          );

          elbow.z =
            0.22 +
            lift * 0.35;

          /*
           * Foot base position.
           */

          const foot =
            radial
              .clone()
              .multiplyScalar(2.15);

          /*
           * Actual walking swing.
           */

          foot.add(
            movementDirection
              .clone()
              .multiplyScalar(
                swing *
                  (0.18 +
                    movementAmount *
                      0.58),
              ),
          );

          /*
           * Small side-to-side movement.
           */

          foot.add(
            tangent
              .clone()
              .multiplyScalar(
                Math.sin(
                  cycle * 0.5,
                ) *
                0.055,
              ),
          );

          /*
           * Foot rises during the
           * swing phase.
           */

          foot.z =
            -0.10 +
            lift;

          /*
           * Forward legs get a little
           * more reach than rear legs.
           */

          const frontBias =
            Math.cos(
              leg.baseAngle,
            );

          foot.add(
            radial
              .clone()
              .multiplyScalar(
                frontBias *
                  movementAmount *
                  0.18,
              ),
          );

          /*
           * Make the lower joint more dynamic.
           */

          elbow.x +=
            movementDirection.x *
            lift *
            0.18;

          elbow.y +=
            movementDirection.y *
            lift *
            0.18;

          /*
           * Draw the articulated leg.
           */

          placeCylinder(
            leg.upper,
            base,
            elbow,
          );

          placeCylinder(
            leg.lower,
            elbow,
            foot,
          );

          leg.joint.position.copy(
            elbow,
          );

          leg.tip.position.copy(
            foot,
          );

          /*
           * Tiny joint pulse while moving.
           */

          const jointScale =
            1 +
            lift *
              0.65;

          leg.joint.scale.setScalar(
            jointScale,
          );

          leg.tip.scale.setScalar(
            1 +
              lift *
                0.9,
          );
        },
      );

      /*
       * -------------------------------------------------------
       * Click pulse
       * -------------------------------------------------------
       */

      const now =
        performance.now() / 1000;

      const pulseAge =
        now - pulseTime;

      if (
        pulseAge >= 0 &&
        pulseAge < 0.55
      ) {
        const progress =
          pulseAge / 0.55;

        pulse.scale.setScalar(
          1 +
            progress * 6,
        );

        (
          pulse.material as THREE.MeshBasicMaterial
        ).opacity =
          0.55 *
          (1 - progress);
      } else {
        (
          pulse.material as THREE.MeshBasicMaterial
        ).opacity = 0;
      }

      /*
       * -------------------------------------------------------
       * Camera drift
       * -------------------------------------------------------
       */

      camera.position.x +=
        (
          pointer.x * 0.7 -
          camera.position.x
        ) *
        0.015;

      camera.position.y +=
        (
          pointer.y * 0.45 -
          camera.position.y
        ) *
        0.015;

      camera.lookAt(
        0,
        0,
        0,
      );

      renderer.render(
        scene,
        camera,
      );

      requestAnimationFrame(
        animate,
      );
    };

    /*
     * ---------------------------------------------------------
     * Resize
     * ---------------------------------------------------------
     */

    const handleResize = () => {
      camera.aspect =
        window.innerWidth /
        window.innerHeight;

      camera.updateProjectionMatrix();

      renderer.setSize(
        window.innerWidth,
        window.innerHeight,
      );

      renderer.setPixelRatio(
        Math.min(
          window.devicePixelRatio,
          1.6,
        ),
      );
    };

    window.addEventListener(
      "resize",
      handleResize,
    );

    animate();

    /*
     * ---------------------------------------------------------
     * Cleanup
     * ---------------------------------------------------------
     */

    return () => {
      destroyed = true;

      window.removeEventListener(
        "resize",
        handleResize,
      );

      window.removeEventListener(
        "pointermove",
        handlePointerMove,
      );

      window.removeEventListener(
        "pointerdown",
        handlePointerDown,
      );

      particleGeometry.dispose();
      particleMaterial.dispose();

      networkGeometry.dispose();
      networkMaterial.dispose();

      ringGroup.traverse(
        (object) => {
          if (
            object instanceof THREE.Mesh
          ) {
            object.geometry.dispose();

            if (
              Array.isArray(
                object.material,
              )
            ) {
              object.material.forEach(
                (material) =>
                  material.dispose(),
              );
            } else {
              object.material.dispose();
            }
          }
        },
      );

      arcGroup.traverse(
        (object) => {
          if (
            object instanceof THREE.Mesh
          ) {
            object.geometry.dispose();

            if (
              Array.isArray(
                object.material,
              )
            ) {
              object.material.forEach(
                (material) =>
                  material.dispose(),
              );
            } else {
              object.material.dispose();
            }
          }
        },
      );

      creature.traverse(
        (object) => {
          if (
            object instanceof THREE.Mesh
          ) {
            object.geometry.dispose();

            if (
              Array.isArray(
                object.material,
              )
            ) {
              object.material.forEach(
                (material) =>
                  material.dispose(),
              );
            } else {
              object.material.dispose();
            }
          }
        },
      );

      renderer.dispose();

      if (
        mount.contains(
          renderer.domElement,
        )
      ) {
        mount.removeChild(
          renderer.domElement,
        );
      }
    };
  }, []);

  return (
    <div
      ref={mountRef}
      aria-hidden="true"
      style={{
        position: "fixed",
        inset: 0,
        pointerEvents: "none",
        zIndex: 0,
        overflow: "hidden",
      }}
    />
  );
}