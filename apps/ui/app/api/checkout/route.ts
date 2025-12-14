import Stripe from 'stripe';
import { NextResponse } from 'next/server';

const stripe = process.env.STRIPE_SECRET_KEY 
  ? new Stripe(process.env.STRIPE_SECRET_KEY, {
      apiVersion: '2025-11-17.clover' as any,
    })
  : null;

let proPriceId: string | null = null;

async function getOrCreateProPrice(): Promise<string> {
  if (!stripe) throw new Error('Stripe is not configured');
  if (proPriceId) return proPriceId;

  const products = await stripe.products.list({ limit: 100 });
  let proProduct = products.data.find(p => p.name === 'Centra Pro Plan');

  if (!proProduct) {
    proProduct = await stripe.products.create({
      name: 'Centra Pro Plan',
      description: 'For growing teams - up to 25 team members, unlimited work items, advanced AI routing, priority support, custom integrations, and analytics dashboard.',
    });
  }

  const prices = await stripe.prices.list({ product: proProduct.id, limit: 100 });
  let proPrice = prices.data.find(p => p.unit_amount === 4900 && p.currency === 'usd' && p.recurring?.interval === 'month');

  if (!proPrice) {
    proPrice = await stripe.prices.create({
      product: proProduct.id,
      unit_amount: 4900,
      currency: 'usd',
      recurring: { interval: 'month' },
    });
  }

  proPriceId = proPrice.id;
  return proPriceId;
}

export async function POST(req: Request) {
  if (!stripe) {
    return NextResponse.json(
      { error: 'Stripe is not configured' },
      { status: 503 }
    );
  }

  try {
    const { plan, billingCycle } = await req.json();
    const priceId = await getOrCreateProPrice();
    const origin = req.headers.get('origin') || 'http://localhost:3000';

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      ui_mode: 'embedded',
      return_url: `${origin}/billing?success=true&session_id={CHECKOUT_SESSION_ID}`,
    });

    return NextResponse.json({ clientSecret: session.client_secret });
  } catch (error) {
    console.error('Stripe checkout error:', error);
    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}
