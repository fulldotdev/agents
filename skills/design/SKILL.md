---
name: design
description: Always use when designing, building, or reviewing interfaces, websites, emails, product flows, or any other visual output.
---

# Design

Make the user's task clear and easy to complete. Follow the existing product, brand, design system, supplied design, and real content. Use the Figma or component skills for tool instructions.

## Start from what exists

- The current site or product is the reference. Screenshot the section you are changing before you touch it, and keep that screenshot next to the result.
- Reuse existing components, blocks, tokens, and spacing. Add a variant or interaction only when this task needs it. For a new section, start from a shadcnblocks block that fits, then bring it in line with the existing components and tokens.
- Do not rebuild a page or a site to change it. Evolve one section at a time.
- Prefer fewer steps and choices over more explanation.

## Keep it plain

- Skip decoration without a purpose: gradients, badges, small labels above headings, uppercase or mono metadata, numbered markers where nothing is a sequence, icon tiles, nested cards, oversized headings, repeated calls to action, appended arrows, animation on every card. Keep them when they are a deliberate part of the supplied design or brand.
- Use concrete labels and truthful content. Do not invent testimonials, statistics, customer logos, features, or extra sections to fill a layout. Placeholders must look like placeholders.

## Picking blocks

- Pick blocks from their screenshots, then read the source before installing: reject blocks that override the button shape, need extra packages, embed video, or need numbers and logos we do not have.
- Neighbouring sections with the same job come from one block family (same image treatment, list markers, heading sizes). Do not mix a bordered block with an open one.
- The header must fit the hero: no hero background pattern or image unless the header sits on it too.
- Dark sections are edge to edge. No card, band or rounded panel inside a dark section; the closing CTA and the footer share the same darkness.
- Interface screenshots only work in showcase grids. In split sections use a photo crop of the work, never a cropped screenshot with cut text.
- Do not show the same photo in two sections.
- Read the block's limits before choosing: a hard cap (`slice(0, 6)`) or a bottom fade hides real content; a CommonJS package (react-fast-marquee) breaks the server build. Prefer a block with props; a block without props gets only its data array and visible strings filled in.
- After installing, diff the block against the registry (`pnpm check:blocks` in full.dev) so the "untouched" rule is checked, not assumed.

## Loop per section

1. Build one section, not a page.
2. Render it and take screenshots at 390, 768, and 1440 wide. If screenshots are not possible, stop and say so instead of continuing blind.
3. Compare with the before screenshot and the reference. Check alignment, spacing, wrapping, hierarchy, primary action, and that only tokens and existing components are used.
4. Run the project's lint and design lint and fix every error.
5. Show the user before and after together, with what changed in one or two sentences.

## Learn from corrections

When the user rejects something twice, add the rule here or, when it is mechanical, to the project's lint config or a reference component.
