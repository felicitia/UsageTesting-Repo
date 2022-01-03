### IR merging -- SCREEN ###

1. account_guest --> account
2. error --> popup
3. filter_option --> filter
4. filter_sort --> filter
5. interests --> get_started
6. password --> sign_in / sign_up
7. username --> sign_in / sign_up

### IR merging -- WIDGET ###

1. bypass --> continue
2. filter_color --> filter_option
3. filter_location --> filter_option
4. filter_price --> filter_option
5. filter_rating --> filter_option
6. filter_sort --> filter_option
7. firstname --> name
8. lastname --> name
9. fullname --> name
10. interests --> bookmark
11. perms_allow --> apply
13. promo --> popup
14. alert --> popup
15. promo_checkbox --> checkbox
16. save --> apply
17. skip --> continue
18. to_signin --> to_signin_or_signup
19. to_signup --> to_signin_or_signup


### Tasks ###

1. check IR merging above to see if it makes sense, and if anything should be changed -- discuss with yixue if unsure
2. once the IR merging is finalized, update the [final labels](https://github.com/felicitia/UsageTesting-Repo/blob/master/IR/final_labels_all.csv) with respect to the IR merging changes -- the final labels are the new ones where we could do multiple labels (but I manually checked and picked the most accurate label, so there shouldn't be any multi-labels anymore)
3. update the [IR screen definition](https://github.com/felicitia/UsageTesting-Repo/blob/master/IR/screen_ir.csv) and [IR widget definition](https://github.com/felicitia/UsageTesting-Repo/blob/master/IR/widget_ir.csv) to reflect the IR merging changes as well
4. double check (2) final labels and (3) IR definitions to make sure it's consistent, e.g., all the labels in the final_labels should be in our definitions, all screen labels should NOT be empty (since no cropping error for screens, but some widget labels can be empty)
