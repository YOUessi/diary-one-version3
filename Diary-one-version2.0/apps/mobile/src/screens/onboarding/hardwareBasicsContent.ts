import type { ComponentProps } from 'react';
import type { OnboardingHeroArt } from '../../components/OnboardingHeroArt';

type ArtKind = ComponentProps<typeof OnboardingHeroArt>['kind'];

export const HARDWARE_BASICS: Array<{
  index: number;
  eyebrow: string;
  title: string;
  lead: string;
  art: ArtKind;
  calloutTitle: string;
  calloutBody: string;
  primary: string;
}> = [
  {
    index: 1,
    eyebrow: 'DEVICE BASICS · 1 OF 7',
    title: 'Wear Diary One',
    lead: 'Diary One captures small parts of your day and turns them into memories worth revisiting.',
    art: 'wear',
    calloutTitle: 'Wear it naturally',
    calloutBody: 'Place Diary One comfortably on your ear with the camera facing forward.',
    primary: 'Continue',
  },
  {
    index: 2,
    eyebrow: 'DEVICE BASICS · 2 OF 7',
    title: 'Power & Volume',
    lead: 'Power and volume controls are on the rear side of Diary One.',
    art: 'power',
    calloutTitle: 'Power · Volume',
    calloutBody:
      'Use the rear Power button and Volume + / −. Voice feedback confirms power state; no press duration is assumed here.',
    primary: 'Continue',
  },
  {
    index: 3,
    eyebrow: 'DEVICE BASICS · 3 OF 7',
    title: 'Choose Your Capture',
    lead: 'Use the left return-to-center wheel to choose Photo, Quick Video, or Long Video.',
    art: 'capture_modes',
    calloutTitle: 'Photo → Quick → Long',
    calloutBody:
      'Up increases Photo → Quick → Long. Down moves Long → Quick → Photo. The wheel does not loop.',
    primary: 'Continue',
  },
  {
    index: 4,
    eyebrow: 'DEVICE BASICS · 4 OF 7',
    title: 'Double Tap to Capture',
    lead: 'Use the left touch surface when you deliberately want to capture something.',
    art: 'double_tap',
    calloutTitle: 'Double tap',
    calloutBody:
      'In Photo mode, Double Tap takes a photo. In video modes, Double Tap starts recording; Double Tap again can end it early.',
    primary: 'Continue',
  },
  {
    index: 5,
    eyebrow: 'DEVICE BASICS · 5 OF 7',
    title: 'Adjust Your View',
    lead: 'Use the right three-position dial to change the camera angle.',
    art: 'angle',
    calloutTitle: 'Forward · Down · Camera Hidden',
    calloutBody: 'Forward = 0°. Down = −15°. Camera Hidden = +90° and visual capture is paused.',
    primary: 'Continue',
  },
  {
    index: 6,
    eyebrow: 'DEVICE BASICS · 6 OF 7',
    title: 'Automatic Capture',
    lead: 'Diary One can capture short samples in the background while you go about your day.',
    art: 'auto',
    calloutTitle: 'Standard automatic capture',
    calloutBody: 'About 9 seconds every 2 minutes. It is not continuous recording.',
    primary: 'Continue',
  },
  {
    index: 7,
    eyebrow: 'DEVICE BASICS · 7 OF 7',
    title: 'From Recordings to Memories',
    lead: 'Recordings become useful only after they are synced and processed into memories.',
    art: 'pipeline',
    calloutTitle: 'Sync → Understand → Remember',
    calloutBody:
      'Sync transfers recordings, cloud processing understands/selects/organizes them, and Diary keeps meaningful memories plus your manual Originals.',
    primary: 'Open Diary',
  },
];
