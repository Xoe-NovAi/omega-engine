# Carmack on Rage — Game Developer Interview (August 2011)
**Source**: https://www.gamedeveloper.com/design/carmack-on-i-rage-i-

## Mobile Technology → PC Pipeline

> "The last iOS Rage project, we shipped with some new technology that's using some clever stuff to make live C++ objects that live in memory mapped files, backed by the flash file system on here, which is how I want to structure all our future work on PCs."

## Biggest Mistake of the Generation

> "Because what I look back as one of the biggest mistakes I made in this generation, was at the beginning, five or six years ago, looking and saying, 'Consoles are basically as good as PCs,' at the time, and developing the workflow so it worked across both of them."

> "Looking back now, we have PCs that are an order of magnitude more powerful, and if our workflow is instead focused on explicitly on just... you build and develop on the PC, and you decimate things into a target for the consoles. There are things that I would do very differently."

## The Three Legs of Modern Development

Massive cores (24 threads), massive memory (24GB), solid state drives (0.5TB). Taking this as the development baseline:

> "My marching orders to myself here are, I want game loads of two seconds on our PC platform, so we can iterate that much faster."

The mobile-derived solution:

> "Everything is going to be decimated and used in relative addresses, so you just say, 'Map the file, all my resources are right there, and it's done in 15 milliseconds.' That's actually how we shipped the last iOS title."

## Integrated Graphics

> "And of course the inevitability is that the integrated graphics cards are getting better, and it's not going to be too long before those provide a good enough solution. We're working closely with Intel, actually, on this. Because we expect Rage to be able to run 30 frames per second on Sandy Bridge cards."
