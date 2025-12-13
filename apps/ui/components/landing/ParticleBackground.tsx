"use client";

import { useEffect, useMemo, useState } from "react";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { type Container, type ISourceOptions } from "@tsparticles/engine";
import { loadSlim } from "@tsparticles/slim";

export default function ParticleBackground() {
    const [init, setInit] = useState(false);

    useEffect(() => {
        initParticlesEngine(async (engine) => {
            await loadSlim(engine);
        }).then(() => {
            setInit(true);
        });
    }, []);

    const particlesLoaded = async (container?: Container): Promise<void> => {
        console.log(container);
    };

    const options: ISourceOptions = useMemo(
        () => ({
            background: {
                color: {
                    value: "#020202",
                },
            },
            fpsLimit: 120,
            interactivity: {
                detectsOn: "canvas",
                events: {
                    onClick: {
                        enable: true,
                        mode: "push",
                    },
                    onHover: {
                        enable: true,
                        mode: "repulse",
                    },
                    resize: {
                        enable: true,
                        delay: 0.5
                    },
                },
                modes: {
                    grab: {
                        distance: 400,
                        links: {
                            opacity: 1,
                        },
                    },
                    bubble: {
                        distance: 400,
                        size: 40,
                        duration: 2,
                        opacity: 8,
                        speed: 3,
                    },
                    repulse: {
                        distance: 200,
                        duration: 0.4,
                    },
                    push: {
                        quantity: 4,
                    },
                    remove: {
                        quantity: 2,
                    },
                },
            },
            particles: {
                color: {
                    value: "#ffffff",
                },
                shape: {
                    type: "circle",
                },
                opacity: {
                    value: 0.5,
                    animation: {
                        enable: false,
                        speed: 1,
                        sync: false,
                    },
                },
                size: {
                    value: 3,
                    animation: {
                        enable: false,
                        speed: 40,
                        sync: false,
                    },
                },
                links: {
                    enable: true,
                    distance: 150,
                    color: "#ffffff",
                    opacity: 0.4,
                    width: 1,
                },
                move: {
                    enable: true,
                    speed: 6,
                    direction: "none",
                    random: false,
                    straight: false,
                    outModes: {
                        default: "out",
                    },
                    attract: {
                        enable: false,
                        rotateX: 600,
                        rotateY: 1200,
                    },
                },
                number: {
                    density: {
                        enable: true,
                        width: 800,
                        height: 800, // value_area
                    },
                    value: 80,
                },
            },
            detectRetina: true,
        }),
        [],
    );

    if (init) {
        return (
            <Particles
                id="tsparticles"
                particlesLoaded={particlesLoaded}
                options={options}
                className="absolute inset-0 -z-10"
            />
        );
    }

    return <></>;
}
