"use client";

import { motion } from "framer-motion";
import ParticleBackground from "@/components/landing/ParticleBackground";
import Link from "next/link";
import { ArrowRight, Brain, TrendingUp, Shield, Zap, CheckCircle2, BarChart3, Clock, Users, FileSearch, Layers } from "lucide-react";

export default function LandingPage() {
    const features = [
        {
            icon: Zap,
            title: "Ingest & Contextualize",
            description: "Centra connects to your observability and ticketing stacks (DataDog, PagerDuty, Jira) to build a real-time graph of your engineering ecosystem."
        },
        {
            icon: Brain,
            title: "Decision Engine",
            description: "Our LLM-based engine analyzes incident logs, service dependencies, and on-call schedules to determine the best possible owner."
        },
        {
            icon: CheckCircle2,
            title: "Automated Routing",
            description: "Work is automatically assigned with a confidence score and a natural language explanation of why this person was chosen."
        },
        {
            icon: TrendingUp,
            title: "Reinforcement Learning",
            description: "The system learns from every override, transfer, and resolution, constantly refining its model to reduce noise and misrouting."
        }
    ];

    const benefits = [
        {
            icon: Clock,
            title: "Slash Resolution Times",
            description: "Cut MTTR by 50% by eliminating routing bounce. The right expert gets the ticket instantly, not 3 hops later."
        },
        {
            icon: Users,
            title: "Prevent Burnout",
            description: "Smart load balancing ensures no single engineer is overwhelmed, keeping your team fresh and effective."
        },
        {
            icon: FileSearch,
            title: "Full Context",
            description: "Tickets are enriched with recent deployments, related errors, and runbooks so the fix can start immediately."
        },
        {
            icon: Layers,
            title: "Zero-Touch Integration",
            description: "Connects seamlessly with your existing stack—Jira, PagerDuty, Slack, and GitHub—in minutes."
        }
    ];

    return (
        <div className="relative min-h-screen w-full overflow-hidden selection:bg-white/20">
            {/* Background Particles */}
            <ParticleBackground />

            {/* Hero Section */}
            <section className="relative z-20 min-h-screen flex flex-col items-center justify-center px-4 text-center pt-20">
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
                    Intelligent incident routing that learns from your team and gets smarter everytime
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7, duration: 0.5 }}
                    className="mt-12 pointer-events-auto"
                >
                    <Link href="/sign-up">
                        <button className="group relative px-8 py-4 bg-white text-black rounded-full transition-all hover:scale-105 font-medium">
                            <span className="relative flex items-center gap-2">
                                Get Started
                                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                            </span>
                        </button>
                    </Link>
                </motion.div>
            </section>

            {/* How It Works Section */}
            <section className="relative z-20 py-24 px-4 bg-black/40">
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
                            A complete intelligence loop for your engineering operations.
                        </p>
                    </motion.div>

                    <div className="flex flex-col lg:flex-row gap-12 items-center">
                        {/* Left: Stacked Features */}
                        <div className="flex flex-col gap-6 w-full lg:w-1/2">
                            {features.map((feature, index) => {
                                const Icon = feature.icon;
                                return (
                                    <motion.div
                                        key={feature.title}
                                        initial={{ opacity: 0, x: -50 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        viewport={{ once: true, margin: "-50px" }}
                                        transition={{ duration: 0.6, delay: index * 0.1, ease: "easeOut" }}
                                        className="bg-zinc-900/50 backdrop-blur-md border border-white/5 rounded-2xl p-6 hover:bg-zinc-800/50 hover:border-white/10 transition-all group"
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className="p-3 bg-white/5 rounded-xl group-hover:bg-white/10 transition-colors flex-shrink-0">
                                                <Icon className="h-6 w-6 text-white" />
                                            </div>
                                            <div>
                                                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                                                <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
                                            </div>
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </div>

                        {/* Right: Dashboard Image */}
                        <div className="w-full lg:w-1/2">
                            <motion.div
                                initial={{ opacity: 0, x: 50, scale: 0.95 }}
                                whileInView={{ opacity: 1, x: 0, scale: 1 }}
                                viewport={{ once: true, margin: "-100px" }}
                                transition={{ duration: 0.8 }}
                                className="relative rounded-xl border border-white/10 shadow-2xl overflow-hidden bg-black/50 backdrop-blur-xl group"
                            >
                                <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
                                <img
                                    src="/dashboard-preview.png"
                                    alt="Centra Dashboard"
                                    className="w-full h-auto rounded-xl opacity-90 hover:opacity-100 transition-opacity duration-500"
                                />
                                {/* Glass Reflection Effect */}
                                <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none rounded-xl"></div>
                            </motion.div>
                        </div>
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
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                            Why Centra?
                        </h2>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {benefits.map((benefit, index) => {
                            const Icon = benefit.icon;
                            return (
                                <motion.div
                                    key={benefit.title}
                                    initial={{ opacity: 0, y: 30 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true, margin: "-50px" }}
                                    transition={{ duration: 0.7, delay: index * 0.1, ease: "easeOut" }}
                                    className="flex flex-col items-center text-center p-8 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl hover:bg-white/10 transition-all hover:scale-[1.02]"
                                >
                                    <div className="p-4 bg-white/10 rounded-full mb-6">
                                        <Icon className="h-8 w-8 text-white" />
                                    </div>
                                    <h3 className="text-2xl font-semibold text-white mb-3">
                                        {benefit.title}
                                    </h3>
                                    <p className="text-gray-400 text-lg leading-relaxed max-w-sm">
                                        {benefit.description}
                                    </p>
                                </motion.div>
                            );
                        })}
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
                        <div className="pointer-events-auto">
                            <Link href="/sign-up">
                                <button className="group relative px-8 py-4 bg-white text-black rounded-full transition-all hover:scale-105 font-medium">
                                    <span className="relative flex items-center gap-2">
                                        Get Started
                                        <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
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
