---
id: int-2011-rage-001
type: interview
tier: 2
confidence: 8/10
title: "Carmack on Rage"
date: 2011-08-19
project: "Rage"
keywords: ["MegaTexture", "framerate", "static code analysis", "PC vs Console", "iPhone"]
source_url: "https://www.gamedeveloper.com/design/carmack-on-i-rage-i-"
fetched_at: "2026-07-01T16:00:00Z"
fetched_by: "John Carmack entity"
source_hash: "sha256:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
word_count: 2100
status: ingested
---

# 🔱 Carmack on Rage
# ⬡ OMEGA ⬡ john_carmack ⬡ INTERVIEW ⬡ 2011

## Verbatim Text

[The legendary programmer speaks to Gamasutra about finishing up work on id's latest game, what's going on with Doom 4, his mistaken predictions for the technology landscape, and the advantages of coding for iPad and consoles over PC.]

John Carmack is synonymous with hardcore game programming. Having always pushed the technology boundaries, his latest brainchild -- "MegaTextures" -- are about to get their most prominent push into the wild with the launch id's latest game, Rage, which launches in October.

In this extensive interview, he speaks about the advantages and disadvantages of the id Tech 5 engine which powers Rage, how it is to be under the same banner as Bethesda (and puts to rest as to why the id Tech 5 engine wouldn't work for the developer's upcoming Skyrim).

He also discusses the pros and cons of PC development, how working on the iPad has lead to some technological breakthroughs for his future mainline development, and how he was wrong about the evolution of console and PC gaming technology.

So you're finishing up the game.

John Carmack: We are at that point now where I'm looking back at the things we could do better and the things we will do better with Rage 2.

You're already thinking about that stuff?

JC: Yeah.

How many programmers do you have on Rage?

JC: It's like 15 or 18 on Rage. Which is a large team. Actually, one of the things that I've been spending a lot of time [with] recently is static code analysis of everything. It's interesting when you've got a multi-million line code base with 15 to 20 programmers, plus another dozen on the Doom 4 project. They're all kind of working on the same code base.

One of the humbling things that you find is that, no matter how good of a programmer you are, you write code, and you make stupid mistakes. And I am getting to be a huge proponent of really, really rigorous code analysis, because I have been going through pioneering these things, just squeegeeing through our code base, and every single programmer -- from our best to our worst -- they all make stupid mistakes, and they are unavoidable. So, we need to have more automated checks on these things.

So, you're doing that kind of thing manually?

JC: Well, I'm using tools, obviously.

But they're not automated enough.

JC: Yeah. This is a really interesting thing. So, Microsoft has got some pretty good static analysis tools, and normally they make you buy, like an $8,000 professional edition of Visual Studio, but they give it for free to all Xbox developers -- which I think says an interesting thing about this stuff. Where Microsoft figures that, well, nobody blames them for crappy software on Windows, but they do blame Microsoft a bit for crappy software on 360, so it's in their best interest to put more static analysis tools available there.

I swear, any 360 developer that's not using that is making a mistake. It will find problems in your code base. But after we got through all of that, we made it so it's warnings as errors, nobody can check in anything that doesn't pass that. We've been going on adding additional tools like PVS Studio and PC-Lint.

They start changing the way people program, because some programmers will be like, "That's perfectly legal code. What the hell is it complaining about?" It's complaining about that because it's seen a hundred cases of somebody doing it like that and messing up and doing something wrong afterwards.

You're still very hands-on with all this stuff.

JC: If anything, since the [ZeniMax acquisition], it's been great. I don't even have to pretend to be an executive anymore. I don't have to go to board meetings. I don't have to do anything! I can just sit in my office and work.

My core is defined as being an engineer. I take resources and a goal, and I try and put them to the best use to get us there. That's what I do. I don't want to be doing anything else.

Let's talk a bit about "MegaTexture."

JC: One of the coolest things with the MegaTexture stuff is, at the end of the project, of course, you're always worried about breaking things. You know, any time you add a feature, you have a chance of causing a regression of some kind.

We've got this whole team, our "stamp squad". They use the MegaTexture tools, where they just fly around and they can start sort of painting in the world. As part of the game development process, that is so magical, because it guarantees it doesn't take up any more space, it doesn't cause any slowdowns, and it doesn't cause any bugs. So, we've got this whole corner of the office of guys, and they're just going through to make the game look cooler, and it doesn't have any drawbacks whatsoever. That's been a really awesome part of it.

The real benefit of the direction we took on this is it allows us to be -- at least arguably -- the best looking game. I think we've got vistas that are among the coolest things anybody's seen.

But the key point is, people might argue pro and con relative to another game, we're running at two times the framerate of almost all the competition, and that's something that I'm really personally proud of, because that was a hard-fought battle internally. Because life is just easier when you've got 33 milliseconds instead of 16, but I think it matters. I think I could have made the game look better at 30 hertz. We could have had some more design freedom.

Why is that so important to you?

JC: It's that subtle feel of that... In fact, it's interesting; I did a number of experiments during this, where we say, "Okay. 60 is better than 30. Is 120 better than 60?" And I did some test cases on there, and interestingly, almost nobody can tell the difference between 120 and 60. A few people, like high-end professional gamers, can tell the difference.

I have a buddy who swears he can tell the difference between 120 and 60.

JC: Yeah. There are some people that can tell. But the difference between 30 and 60, there are some people who can't even tell that. "Eh, it looks about the same to me." But most people get at least a subliminal feel about it. It's more responsive. It's crisper. It's smoother.

But it is interesting that that next doubling, going to 120 makes almost no difference, which means that we've got this benefit curve on here, and 60 is kind of right at the knee.

And there's other areas where we're approaching that. You talk about resolution. An iPhone 4 display, that's about at visual acuity on there, where going much higher doesn't make much difference. So, it's kind of a cool thing that in many ways, we are approaching sort of the biological limits of what betterness we can display.

When you're trying to do something like make a game that's 60 frames instead of 30 -- certain things that you do, are they driven by your engineering background? Is it that you want to challenge yourself? Or are you an egotistical man that wants 60 frames over everyone else?

JC: That was a decision where, when I first started off, I was designing a graphics engine that was going to be 30 frames per second. And I got some sense of what I thought I could do there. And then I got some sense of what I could do at 60.

And this is the important point, where I made the conscious decision that the user is going to get more value out of running at a higher framerate than me making the pixels pretty. Because that was the choice. You can go ahead and say, "Well, we can go ahead and pile on some additional levels of stuff here."

There are people who argue the exact opposite quite a bit.

JC: It's certainly a valid argument. It's not a foregone conclusion. Previously, not all, but most of the previous id games made that decision. "We want to show people graphics they've never seen before." That usually meant coming out running at a barely acceptable framerate until people got the next generation of graphics cards that made it really smooth.

I think that games look fabulous today, and I think that we can do a pretty good job of any designer's vision with the technology we've got today. And I think that that delta, of me doing a 30 hertz game versus a 60 hertz one, throwing twice the horsepower at the graphics, I don't think, gives as much to the user as giving it that extra smooth feel.

It's still arguable, because in the Doom 4 project, we decided the multiplayer is 60 frames per second, but the single player is 30 frames per second, so you can have twice as many demons coming at you. They're valid decisions to go each way, but I am proud of the fact that we were able to push Rage through at that field.

And part of it also was because in a driving environment, you notice 60 frames per second a lot more than you do when you're just walking around. So, that was also part of the deal -- it made it more important to be 60 frames per second.

As a renowned programmer, is there any technology out there that you look at that's not id that you're very impressed, like "Wow, how did they do that?"

JC: You know, I'm actually pretty impressed with most of the modern games. I think almost all the big games look really great nowadays.

I think the difference with you guys is the team size, though.

JC: We've grown a lot. We are a lot larger than we used to be. And in fact, one of the real lessons that we learned is Rage took too long for a couple reasons. We rewrote too much technology. We're not going to do that in the future. We're going to be more focused in what we do. And also a lot of the technology, like our animation and some of the AI stuff, was going to be good enough to keep, even if I rewrite the graphics engine.

But the other thing is just once you've made all the decisions, there's real value in being able to pile a hundred people onto a project. Now that id's grown to be multi-team, we should be doing more of that shifting resources around. As soon as Rage ships, the core tech team is going over to help the Doom 4 team. I think that's the more correct way.

If you can have a small team, get a game rolling, kind of lay out the core concepts of the game [you can do that], but if you want to get done in three years, you need to be able to throw a lot of people on it. It's awful trying to hire a bunch of people. You want to be able to have a migratory workforce that can kind of move from project to project, rather than see the whole thing through, because it's a waste to have a hundred people on it for six months of a project, when you don't know what the heck you're doing. But you really would like to throw a lot of resources on it at the end.

How have you made the decision, or has Bethesda made the decision not to license id Tech 5? I talked to Tim [Willits] a little bit about that, but [when we ran the story], there was some disappointment from people.

JC: It's interesting when you look back at our technology licensing -- it was never really a business that I wanted to be in. In the very early days, people would pester us, and we would just throw out some ridiculous terms, and we were surprised that people were taking us up on it.

I didn't want to be in the process of supporting a lot of outside teams -- because we feel beholden to not make radical changes, and pull the rug out from underneath lots of other people. If it's your own team, you can make the sensible decision of "It's going to be worth it. It's going to suck for a while, but we can make our way through it." But you don't want to do that to other people.

People who are paying you.

JC: Yeah. You know, Epic's done a really good job at building up a support structure for all of that. They have done a good job. The market was ours to keep, and we abdicated because we weren't willing to put that kind of effort into it. We didn't want to have half our company be about managing technology licensing. And they've gone and done a great job with it.

Even though we're inside Bethesda... We talk about, well, "id Tech 5 does these things well," but it's not magic. If you have a team that's up to speed and is going great guns with Unreal Technology, I don't care at all. It's not a personal affront to me if somebody wants to choose a different technology to build a game upon.

There are certain things that I think we do better than anybody else. If you want to be an awesome looking, 60 frames per second game... If you want to be able to craft a world around this kind of extraordinary detail, we're better than anything.

But there are some things it's bad on. If you wanted to do the next Grand Theft Auto that had a city... It's too much surface area to MegaTexture everything at the level of detail that you want to do. If you want to do a game that's all about walking around with torches, our dynamic lighting approximations are not as good as you might want for something like that.

There are certainly aspects in which you put the best programmers [on a project] and give them lots of resources, and they do something great for this targeted thing, but there are so many decisions you can make. You can't make something that's the best for everyone.

The MegaTexture direction gives us some big wins, but it's also fairly restrictive on certain types of games. It would be a completely unacceptable engine to do [Bethesda's Elder Scrolls V] Skyrim in, where you've got the whole world going, and you're walking across these huge areas.

What about mobile? You've got your iPad there, and I know that you did [Rage HD](http://itunes.apple.com/app/rage-hd/id400707675?mt=app)... Is that almost a pet project for you?

JC: I think Zenimax humors me about it, because Zenimax proper is all about swinging for the fences. [laughs]

But you're always about the new stuff and tinkering with that.

JC: Yeah. And I actually get multiple benefits out of it in that... The last iOS Rage project, we shipped with some new technology that's using some clever stuff to make live C++ objects that live in memory mapped files, backed by the flash file system on here, which is how I want to structure all our future work on PCs.

Because what I look back as one of the biggest mistakes I made in this generation, was at the beginning, five or six years ago, looking and saying, "Consoles are basically as good as PCs," at the time, and developing the workflow so it worked across both of them.

Looking back now, we have PCs that are an order of magnitude more powerful, and if our workflow is instead focused on explicitly on just... you build and develop on the PC, and you decimate things into a target for the consoles. There are things that I would do very differently.

And part of that stuff is, the three legs of this that we have now, is we have massive numbers of cores -- I have 24 threads on my desktop machine. Massive amounts of memory -- 24 gigs, and we can throw a lot more in. And we've got solid state drives -- you can put a half of a terabyte in there. And if I take that as the baseline of what I want all our developers to use, I will build a very different system.

My marching orders to myself here are, I want game loads of two seconds on our PC platform, so we can iterate that much faster. And right now, even with solid state drives, you're dominated by all the things that you do at loading times, so it takes this different discipline to be able to say "Everything is going to be decimated and used in relative addresses," so you just say, "Map the file, all my resources are right there, and it's done in 15 milliseconds."

That's actually how we shipped the last iOS title. Most of the stuff was set up like that. I'm excited to be carrying that forward. That was great. So, that wasn't a throwaway research project. That was a product that went out and made money. It's nice to be able to do things like that.

How has it been working on a multiplatform title these days? 

JC: I did a bunch of console stuff, with Super Nintendo, 32X, and Jaguar and all that stuff before. There's different vibes with it, where it's fun to be able and go and say -- on the PS3, you can be like, "Here are registers. You can go ahead and hit the hardware like this. Watch out for these DMA faults, and watch out for the awful low level stuff there." But it is nice to be able to say, "We've got 512 megs here. The OS takes 32 megs of it. We're looking at mapping out all our regions on there."

It's pretty sad, the fact that we have these PCs that are sometimes 10 times as powerful, and we have more trouble holding 60 frames per second on the PCs because of drive and OS unoptimalities. And there are reasons for all of them. I've done enough driver work on OpenGL to understand why things wind up the way they are.

And sure, on the PC, you can go ahead and you're running two megapixels. You can turn on anti-aliasing, and you can have much bigger page tables for the virtual textures, and all this stuff. But still, if you want it to get done in like 16 milliseconds, the graphics drivers are a huge hindrance right there.

So, PC development right now is just so different than it was before this console generation. Do you ever wish that "core" PC gaming wasn't so -- well, I don't want to say "marginalized"...

JC: When you look at all the MMO money on there, there's still a lot. And when you include Facebook games and stuff like that, all the web games.

It's just, I think people regret the migration of the hardcore action game, which clearly has taken a move towards the consoles. But gaming on the PC, there's probably more hours of PC games going on now than there were five years ago. There's expansion in the market, different trends, and things like that. And sometimes, just the world doesn't always correspond to your wishes. There are large market forces that happen.

So, I miss some of the aspects of the PC, about pushing for the latest and greatest -- you know, giving people a reason to want a $500 video card. I did always enjoy that a little bit, that sense of, "Here's something that's cool, but it will be so much cooler if you buy the latest and greatest."

It doesn't make sense now. I have a PC that I built in 2007. It's nothing fancy at all, and it can still run the latest [DX9] Crysis, full out.

JC: And of course the inevitability is that the integrated graphics cards are getting better, and it's not going to be too long before those provide a good enough solution. We're working closely with Intel, actually, on this. Because we expect Rage to be able to run 30 frames per second on Sandy Bridge cards. Which is not as good as the consoles, but it's a start. People will be able to play the game, experience it, and look at it there.

I'm a bit of a fan of the integration of greater and greater power there. Certainly with AMD's upcoming Fusion stuff, it's a foregone conclusion that that's going to get pretty powerful. And because we again talk about the knee of the graphics curve on there, where even if you can get a ten times more powerful add-in card there, unless people go and dedicate and build their media around that, it's going to be this somewhat marginal incremental improvement overall.

We're not there yet. If you want to experience Rage on a PC at its full glory, you still want to add a graphics card. But as we get to future titles, it's going to be less and less pull for that high end stuff.

Now, if you set me down and say, "Everybody's got this monster dual card, high-end system," you know, I could do some awesome stuff on that! But then you'd have to have artists make more and more awesome stuff, and you're winding up with a $100 million game budget that you're going to lose your shirt on.

We talked about the consoles that Rage is coming out for. Are you interested in the Wii and 3DS? Did you see the new Wii U?

JC: I haven't been over there yet. You know, interestingly I have a six-year-old son now. The only games I play at home are Wii and DS games. I'm an old-school Mario fan, and all that. I don't play the hardcore shooters. Some of that is because, when you see how the sausage is made, you're not quite as excited about that. I kind of like the pure and simple games because I don't have ten hours over the weekend to spend gaming, but I do have fun sitting down and playing simple things.

Many, many years ago, we had negative experiences with Nintendo, but the only reason we're not doing anything with Nintendo now is just that the technologies are out of sync. It's a perfect opportunity to do PC, 360, PS3, but you couldn't have the same content base also targeting the Wii. But, you know, the new platform is probably just right there. It would probably be straightforward to target our stuff over there. It would depend on what the business case is for any of that.
