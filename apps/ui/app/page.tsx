"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import ParticleBackground from "@/components/landing/ParticleBackground";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function LandingPage() {

    return (
        <div className="relative min-h-screen w-full overflow-hidden selection:bg-white/20">
            {/* Background Particles */}
            <ParticleBackground />

            {/* Hero Section */}
            <main className="relative z-20 flex min-h-screen flex-col items-center justify-center px-4 text-center pointer-events-none">

                {/* Animated Reveal Text */}
                <motion.h1
                    initial={{ opacity: 0, y: 20, filter: "blur(10px)" }}
                    animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="max-w-4xl text-7xl font-bold tracking-tighter md:text-9xl lg:text-[12rem] bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60 pointer-events-none"
                >
                    Centra
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3, duration: 0.8 }}
                    className="mt-6 max-w-2xl text-lg text-gray-400 md:text-2xl font-mono pointer-events-none"
                >
                    The Operating System for Intelligence.
                </motion.p>

                {/* Breathing Button */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.6, duration: 0.5 }}
                    className="mt-12 pointer-events-auto"
                >
                    <Link href="/dashboard">
                        <button className="group relative px-8 py-4 bg-transparent overflow-hidden rounded-full transition-all hover:scale-105">
                            <div className="absolute inset-0 border border-white/20 rounded-full group-hover:border-white/50 transition-colors"></div>
                            <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-full blurred-bg"></div>

                            {/* Breathing Glow */}
                            <div className="absolute inset-0 rounded-full animate-pulse-slow border border-white/10 filter blur-[1px]"></div>

                            <span className="relative flex items-center gap-2 font-medium tracking-wide text-lg">
                                START SEQUENCE
                                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                            </span>
                        </button>
                    </Link>
                </motion.div>

            </main>
        </div>
    );
}
