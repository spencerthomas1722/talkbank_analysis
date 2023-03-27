# talkbank_analysis
 Cross-sectional and longitudinal analysis of data from the TalkBank database

# Introduction
Some autistics start using words much later than their TD peers, and take longer to reach further linguistic milestones like multi-word utterances. (The spectrum is broad, however. An autistic cousin of mine didn't speak until she was 3, and didn't form sentences until she was 5. On the other hand, I am also autistic, and I was saying words by 9 months and simple sentences by 18 months.)
In order to gauge each child's general linguistic development, I analyzed vocabulary size/variation with types, tokens, and type/token ratio. I also measured MLU, i.e. sentence length.

Autistic people, particularly children, also have conversational deficits: we don't know how to continue a conversation, or don't even understand that we are expected to do so. For this reason, I hypothesized that the autistic subjects would contribute less to their conversations than their TD peers, and that this would materialize as a lower mean length of turn (MLT). (A *turn* is the amount of words a person says, across one or more utterances, before another person starts talking.)

Autistics also have a tendency for *echolalia*: the repetition of other's utterances.
Specifically, in some of these transcripts, I noticed that a child would repeat part of their interlocutor's utterance, without showing real comprehension: TODO example
So I measured the percentage of each child's utterances that were a partial or full repetition of the other speaker's last utterance. More details can be found in the Analysis section below.

# Data
I mostly focused on the transcripts of six autistic children from [Helen Tager-Flusberg's ASDBank corpus](https://asd.talkbank.org/access/English/Flusberg.html).
These data had a few limitations. Namely, it only includes children who were diagnosed with ASD in the '80s. They were selected through their schools or through home intervention programs that they wree enrolled in. In keeping with diagnostic trends of the era, they were all male. Tager-Flusberg says that they ranged in SES from low to upper-middle class. She makes the following note, which indicates that there may have been some unintentional sampling bias that led to the recruitment of more linguistically capable individuals:
> Although the children were not preselected for higher levels of functioning, in fact five of the six autistic children fell in the normal or low-normal IQ range.
Of course, these children had all developed some language. We do not know much about their linguistic development prior to enrollment in this study, though --- for example, when they reached milestones like their first word.

With that being said, these data are still valuable in comparing the general tendencies of autistic children and typicallly-developing (TD) children. 
In order to get a sense of how each child's development compared to their TD peers, I measured the average of these metrics for 100 TD children in CHILDES. These transcripts, like the ones in the Flusberg corpus, had the activity type tag "toyplay".

# Methods
## Technical details
I collected the transcripts for the TD children using the third-party TalkBank API tbdb.py. 
This API returns transcripts that contain audio/video but no transcript. When I encountered one of these, I substituted it with a new transcript from those not yet used.

The API only allows the user to view word-based data, not any of the dependent tiers. For this reason, my analyses involved tokens, not morphemes. This hurts the depth of my analysis somewhat, but the data still give us a decent view of each child's linguistic abilities.

### Weird bugs
The API also includes a weird bug: getUtterances() returns some utterances many times over. For example, the sentence (a) was returned as (b). The sentence appears nine times, when it should appear once. It also contains underscores only some of the time.

(a) `CHI: have milk_ball please ?`
(b) `['050800', 'asd/English/Flusberg/Brett/050800', 4, 'CHI', 'Target_Child', None, None, 'have milk_ball please', None, None], ['050800', 'asd/English/Flusberg/Brett/050800', 4, 'CHI', 'Target_Child', None, None, 'have milk_ball please', None, None], ['050800', 'asd/English/Flusberg/Brett/050800', 4, 'CHI', 'Target_Child', None, None, 'have milkball please', None, None], ['050800', 'asd/English/Flusberg/Brett/050800', 4, 'CHI', 'Target_Child', None, None, 'have milk_ball please', None, None], ['050800', 'asd/English/Flusberg/Brett/050800', 4, 'CHI', 'Target_Child', None, None, 'have milk_ball please', None, None], ['050800', 'asd/English/Flusberg/Brett/050800', 4, 'CHI', 'Target_Child', None, None, 'have milkball please', None, None], ['050800', 'asd/English/Flusberg/Brett/050800', 4, 'CHI', 'Target_Child', None, None, 'have milk_ball please', None, None], ['050800', 'asd/English/Flusberg/Brett/050800', 4, 'CHI', 'Target_Child', None, None, 'have milkball please', None, None]`

*Note: I had removed punctuation from the sentence (i.e. in the strings "have milk(_)ball please") before viewing this. So I considered that my manipulating the strings may have caused this error. However, upon examining the data returned directly from `getUtterances`, I found that the problem was present before I changed it.*

I noticed this bug because I was seeing some unusually high MLTs --- in the 30-50 range instead of 3-6. 

## Analysis
The metrics I measured were:
* Mean length of utterance (MLU) and mean length of turn (MLT) (`meanlength()`)
	* TalkBank's CHAT commands can calculate this, but doing so was not feasible for the 1600+ transcripts involved in this analysis. So I calculated the MLU and MLT for all transcripts using my own code for the sake of consistency.
* Types, tokens, type-token ratio, and type-utterance ratio (`ttr()`)
	* I measured type-utterance ratio because I noticed that the autistic children's transcripts were longer than the TD children's, which may have skewed their type and token counts. So I decided to calculate this in order to normalize for the length of the transcripts. I did so by multiplying a child's TTR by their MLU: types/tokens \* tokens/utterances = types/utterances.
* Echolalia: the percentage of a child's utterances that were repetitions of another speaker's last utterance (`echoed_utterances()`)
	* `c<m`: 
	* I also calculated the reverse, `m<c` and `m=c`, as well as `=last`: the percentage of all utterances that were the exact same as the previous utterance.
For the purposes of these metrics, any speaker besides the target child was labeled as "Mother" (MOT).

I compared each child with TD children of the same age (in months) at the start of their participation in the study, at the end, and at every birthday in between. For example, Brett was was followed from age 5;8 to 7;6, so I compared him with TD children at ages 5;8, 6, 7, and 7;6.

# Results
Overall, most metrics did not increase or decrease with age, indicating that they may not be strong indicators of linguistic development. With the code as it currently is, it is impossible to tell how much variation there was among groups, since we only have an average.

There was also variation in each metric between the autistic children. As we saw on the general scale, mean-length and vocabulary metrics did not tend to change with age. There was one exception: Rick's MLU and MLT increased significantly, from 1.48 and 1.99 to 2.90 and 3.16, respectively. The older children (Brett, Jack, and Mark) saw less change than the younger ones.

While echolalia did not change with age among TD children, it did with some of the autistic individuals. Stuart, Roger, Rick, and Brett's echolalia metrics decreased significantly over the course of their participation. Echolalia is *not* inherently wrong, nor is it necessarily indicative of linguistic underdevelopment. But the decrease in echolalia indicates that *more* of the child's speech consists of their own thoughts and contributions, so it serves as a proxy for some aspects of cognitive and linguistic development.

# Conclusion
I found, in accordance with my hypothesis, that the autistic subjects consistently had a lower MLT than the TD children. The fact that autistics had a similar or lower MLU seems to correlate with this, although I did not originally predict it. Some of the children showed a decrease in echolalia over time, which supports my idea that it correlates with linguistic development. 

Contrary to my hypothesis, I found that autistics tended to have a similar or slightly larger vocabulary to TD children, although this metric may have been confounded by the differences in transcript length between the two groups. I also found, to my surprise, that most of these metrics did not correlate with age. This leads me to think there may have been issues with how I calculated them; further examination is needed.
## Future work
As stated directly above, more examination of these data are needed to ensure validity of these results. The lack of correlation between metrics and age is especially worthy of scrutiny. 

In her original paper, Tager-Flusberg measured each child's IPSyn as a measure of syntactic complexity. This would be worth calculating and exploring. She also compared the six autistic children here with six childern with Down's syndrome. From my cursory glance at these other children's transcripts and data, there are some interesting data, and it would be worthwhile to compare their data with the autistic children's as Tager-Flusberg did.
There are also some linguistic traits that are more common in autistic people, including pronoun reversal.