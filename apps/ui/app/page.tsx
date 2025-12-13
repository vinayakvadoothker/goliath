"use client";

import { motion } from "framer-motion";
import ParticleBackground from "@/components/landing/ParticleBackground";
import Link from "next/link";
import { ArrowRight, Brain, TrendingUp, Shield, Zap, CheckCircle2, BarChart3 } from "lucide-react";

export default function LandingPage() {
    const features = [
        {
            icon: Brain,
            title: "AI-Powered Routing",
            description: "Intelligently routes incidents to the right person using context-aware decision making. Understands incident details, service relationships, and team expertise."
        },
        {
            icon: TrendingUp,
            title: "Learns from Outcomes",
            description: "Gets smarter with every assignment. When someone completes a task, the system learns. When they transfer it, it learns from that too. Continuous improvement built-in."
        },
        {
            icon: Shield,
            title: "Evidence-Backed Decisions",
            description: "Every routing decision includes clear explanations. See why this person was chosen, what constraints were checked, and confidence scores for full transparency."
        },
        {
            icon: Zap,
            title: "Reduces Misrouting",
                    description: "Stop wasting time on transfers and reassignments. Research shows incorrect assignment can increase time-to-mitigate by 10×. Centra gets it right the first time."
        }
    ];

    const benefits = [
        "Faster incident resolution",
        "Reduced on-call fatigue",
        "Auditable decision trail",
        "Integrates with Jira, PagerDuty, and more"
    ];

    return (
        <div className="relative min-h-screen w-full overflow-hidden selection:bg-white/20">
            {/* Background Particles */}
            <ParticleBackground />

            {/* Hero Section */}
            <section className="relative z-20 min-h-screen flex flex-col items-center justify-center px-4 text-center">
                <motion.h1
                    initial={{ opacity: 0, y: 20, filter: "blur(10px)" }}
                    animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="max-w-4xl text-6xl font-bold tracking-tighter md:text-8xl lg:text-9xl bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60 pointer-events-none"
                >
                    Centra
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3, duration: 0.8 }}
                    className="mt-6 max-w-2xl text-xl text-gray-300 md:text-2xl font-light pointer-events-none"
                >
                    Intelligent incident routing that learns from your team and gets smarter over time.
                </motion.p>

                {/* Sign In / Sign Up Buttons */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7, duration: 0.5 }}
                    className="mt-12 flex flex-col sm:flex-row gap-4 pointer-events-auto"
                >
                    <Link href="/dashboard">
                        <button className="group relative px-8 py-4 bg-white text-black rounded-full transition-all hover:scale-105 font-medium">
                            <span className="relative flex items-center gap-2">
                                Sign In
                                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                            </span>
                        </button>
                    </Link>
                    <Link href="/dashboard">
                        <button className="group relative px-8 py-4 bg-transparent border-2 border-white/30 text-white rounded-full transition-all hover:scale-105 hover:border-white/50 font-medium">
                            <span className="relative flex items-center gap-2">
                                Sign Up
                                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                            </span>
                        </button>
                    </Link>
                </motion.div>
            </section>

            {/* How It Works Section */}
            <section className="relative z-20 py-24 px-4">
                <div className="max-w-7xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-100px" }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                            How It Works
                        </h2>
                        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                            Centra learns from your team's expertise and makes smarter routing decisions over time.
                        </p>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {features.map((feature, index) => {
                            const Icon = feature.icon;
                            return (
                                <motion.div
                                    key={feature.title}
                                    initial={{ opacity: 0, y: 40 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true, margin: "-50px" }}
                                    transition={{ duration: 0.8, delay: index * 0.15, ease: "easeOut" }}
                                    className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all"
                                >
                                    <div className="flex items-start gap-4">
                                        <div className="p-3 bg-white/10 rounded-lg">
                                            <Icon className="h-6 w-6 text-white" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="text-xl font-semibold text-white mb-2">
                                                {feature.title}
                                            </h3>
                                            <p className="text-gray-400 leading-relaxed">
                                                {feature.description}
                                            </p>
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* Benefits Section */}
            <section className="relative z-20 py-24 px-4 bg-black/20">
                <div className="max-w-7xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-100px" }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="text-center mb-12"
                    >
                        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                            Why Centra?
                        </h2>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {benefits.map((benefit, index) => (
                            <motion.div
                                key={benefit}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true, margin: "-50px" }}
                                transition={{ duration: 0.7, delay: index * 0.1, ease: "easeOut" }}
                                className="flex items-center gap-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4"
                            >
                                <CheckCircle2 className="h-5 w-5 text-white flex-shrink-0" />
                                <span className="text-white font-medium">{benefit}</span>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="relative z-20 py-24 px-4">
                <div className="max-w-4xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-100px" }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                    >
                        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                            Ready to Get Started?
                        </h2>
                        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
                            See how Centra can reduce misrouting and speed up incident resolution for your team.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center pointer-events-auto">
                            <Link href="/dashboard">
                                <button className="group relative px-8 py-4 bg-white text-black rounded-full transition-all hover:scale-105 font-medium">
                                    <span className="relative flex items-center gap-2">
                                        View Dashboard
                                        <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                                    </span>
                                </button>
                            </Link>
                            <Link href="/dashboard">
                                <button className="group relative px-8 py-4 bg-transparent border-2 border-white/30 text-white rounded-full transition-all hover:scale-105 hover:border-white/50 font-medium">
                                    <span className="relative flex items-center gap-2">
                                        See How It Works
                                        <BarChart3 className="h-4 w-4 group-hover:rotate-12 transition-transform" />
                                    </span>
                                </button>
                            </Link>
                        </div>
                    </motion.div>
                </div>
            </section>
        </div>
    );
}
