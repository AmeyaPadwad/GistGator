import pygame
from tkinter import filedialog
import pygetwindow as gw
from tkinter.filedialog import asksaveasfile

import gistgator as gg

pygame.init()

fps = 60
timer = pygame.time.Clock()
width = 540
height = 540
screen = pygame.display.set_mode([width, height])


icon = pygame.image.load("Assets\LogoOnly.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("GistGator")

mainMenuImg = pygame.image.load("Assets\Menus\mainMenu.png")
mainMenuHoveredImg = pygame.image.load("Assets\Menus\mainMenuHovered.png")
mainMenu2Img = pygame.image.load("Assets\Menus\menu2.png")
mainMenu2BackHoveredImg = pygame.image.load("Assets\Menus\menu2BackHovered.png")
transcribeHoverImg = pygame.image.load("Assets\Menus/menu2TranscribeHovered.png")
TSAHoveredImg = pygame.image.load("Assets\Menus/menu2TSAHovered.png")
summarizeHoverImg = pygame.image.load("Assets\Menus\menu2SummarizeHovered.png")
SSAHoveredImg = pygame.image.load("Assets\Menus/menu2SSAHovered.png")
noSummaryImg = pygame.image.load("Assets\Menus/menu2NoSummary.png")
upArrowImg = pygame.image.load("Assets/upArrow.png")
upArrowImgPressed = pygame.image.load("Assets/upArrowPressed.png")
downArrowImg = pygame.image.load("Assets/downArrow.png")
downArrowImgPressed = pygame.image.load("Assets/downArrowPressed.png")

fontFileName = pygame.font.Font("Assets\Fonts\AnonymousPro-Bold.ttf", 17)
fontBody = pygame.font.Font("Assets\Fonts\AnonymousPro-Bold.ttf", 18)

menu = True
menu2 = False
clicked = False
showTranscription = False
showSummary = False
showFilename = True
TextBoxTranscriptActive = False
TextBoxSummaryActive = False
centerMenu = True
scrollT = ""
remTextT = []
scrollS = ""
remTextS = []
filename = ""
transcript = ""
summary = ""


def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.rect.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text


def drawMenu():
    global menu, menu2, clicked, filename, centerMenu

    menu2 = False

    screen.blit(mainMenuImg, (0, 0))

    mousePos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    browseButton = pygame.rect.Rect((170, 325, 200, 83))

    if browseButton.collidepoint(mousePos):
        screen.blit(mainMenuHoveredImg, (0, 0))
        if clicks[0] and not clicked:
            filename = filedialog.askopenfilename(
                initialdir="/",
                title="Select a File",
                filetypes=([("all files", "*.*")]),
            )
            filename = filename.replace("/", "\\")
            if len(filename) != 0:
                menu = False
                menu2 = True
            clicked = True
            centerMenu = True


scrollCounterT = 0
scrollCounterS = 0


def reset():
    global transcript, summary
    transcript = ""
    summary = ""


def drawMenu2():
    global filename, menu2, menu, clicked, transcript, summary, screen, width, height, showTranscription, showSummary, centerMenu, scrollT, remTextT, scrollCounterT, scrollS, remTextS, scrollCounterS

    menu = False

    Dispfilename = filename.split("\\")[-1]
    screen = pygame.display.set_mode([width * 2.60, height * 1.35])
    win = gw.getWindowsWithTitle("GistGator")[0]

    if centerMenu:
        win.moveTo(50, 35)

    screen.blit(mainMenu2Img, (0, 0))

    mousePos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    # pygame.draw.rect(screen, "green", (660, 640, 230, 50), 3)
    # if clicks[0]:
    #     print((mousePos))

    transcribeButton = pygame.rect.Rect((245, 45, 235, 85))
    TSAButton = pygame.rect.Rect((285, 630, 155, 60))
    summarizeButton = pygame.rect.Rect((920, 45, 235, 85))
    SSAButton = pygame.rect.Rect((960, 630, 155, 60))
    backButton = pygame.rect.Rect((10, 15, 130, 50))

    if transcribeButton.collidepoint(mousePos):
        screen.blit(transcribeHoverImg, (0, 0))
        if clicks[0] and not clicked:
            showTranscription = True
            if len(transcript) == 0:
                transcript = gg.STT_run(filename)

    if TSAButton.collidepoint(mousePos):
        screen.blit(TSAHoveredImg, (0, 0))
        if clicks[0] and not clicked:
            f = asksaveasfile(
                initialfile="Untitled.txt",
                defaultextension=".txt",
                filetypes=[
                    ("All Files", "*.*"),
                    ("Text Documents", "*.txt"),
                    ("Word Document", "*.docx"),
                ],
            )
            f.write(transcript)
            f.close()

    if summarizeButton.collidepoint(mousePos):
        screen.blit(summarizeHoverImg, (0, 0))
        if clicks[0] and not clicked:
            if len(transcript) != 0:
                summary = gg.inputOutput()
                showSummary = True
            else:
                screen.blit(noSummaryImg, (0, 0))
                textBox = pygame.rect.Rect((660, 650, 250, 70))
                drawText(screen, Dispfilename, "black", textBox, fontFileName)
                pygame.display.flip()
                pygame.time.delay(2000)

    if SSAButton.collidepoint(mousePos):
        screen.blit(SSAHoveredImg, (0, 0))
        if clicks[0] and not clicked:
            f = asksaveasfile(
                initialfile="Untitled.txt",
                defaultextension=".txt",
                filetypes=[
                    ("All Files", "*.*"),
                    ("Text Documents", "*.txt"),
                    ("Word Document", "*.docx"),
                ],
            )
            f.write(summary)
            f.close()

    if backButton.collidepoint(mousePos):
        screen.blit(mainMenu2BackHoveredImg, (0, 0))
        if clicks[0] and not clicked:
            screen = pygame.display.set_mode([width, height])
            win.moveTo(500, 100)
            menu2 = False
            menu = True
            reset()

    if showTranscription:
        textBox = pygame.rect.Rect((100, 175, 525, 420))
        if scrollCounterT == 0:
            remText = drawText(screen, transcript, "black", textBox, fontBody)
            if remTextT == []:
                remTextT.append(remText)
        elif scrollCounterT > 0:
            remText = drawText(
                screen, remTextT[scrollCounterT - 1], "black", textBox, fontBody
            )
            if scrollCounterT > len(remTextT) - 1:
                remTextT.append(remText)

        if scrollT == "up" and scrollCounterT > 0:
            scrollCounterT -= 1
            scrollT = ""
        elif scrollT == "down" and remText != "":
            scrollCounterT += 1
            scrollT = ""

        if remTextT != []:
            downArrowButtonT = pygame.rect.Rect((660, 560, 50, 50))
            upArrowButtonT = pygame.rect.Rect((663, 165, 50, 50))
            if remText != "":
                screen.blit(pygame.transform.scale(downArrowImg, (70, 70)), (650, 550))
                if downArrowButtonT.collidepoint(mousePos):
                    screen.blit(
                        pygame.transform.scale(downArrowImgPressed, (70, 70)),
                        (650, 550),
                    )
                    if clicks[0] and not clicked:
                        scrollCounterT += 1
            if scrollCounterT > 0:
                screen.blit(pygame.transform.scale(upArrowImg, (70, 70)), (650, 150))
                if upArrowButtonT.collidepoint(mousePos):
                    screen.blit(
                        pygame.transform.scale(upArrowImgPressed, (70, 70)), (650, 150)
                    )
                    if clicks[0] and not clicked:
                        scrollCounterT -= 1

    if showSummary:
        textBox = pygame.rect.Rect((775, 175, 525, 420))
        if scrollCounterS == 0:
            remText = drawText(screen, summary, "black", textBox, fontBody)
            if remTextS == []:
                remTextS.append(remText)
        elif scrollCounterS > 0:
            remText = drawText(
                screen, remTextS[scrollCounterS - 1], "black", textBox, fontBody
            )
            if scrollCounterS > len(remTextS) - 1:
                remTextS.append(remText)

        if scrollS == "up" and scrollCounterS > 0:
            scrollCounterS -= 1
            scrollS = ""
        elif scrollS == "down" and remText != "":
            scrollCounterS += 1
            scrollS = ""

        if remTextS != []:
            downArrowButtonS = pygame.rect.Rect((1335, 560, 50, 50))
            upArrowButtonS = pygame.rect.Rect((1340, 165, 50, 50))
            if remText != "":
                screen.blit(pygame.transform.scale(downArrowImg, (70, 70)), (1325, 550))
                if downArrowButtonS.collidepoint(mousePos):
                    screen.blit(
                        pygame.transform.scale(downArrowImgPressed, (70, 70)),
                        (1325, 550),
                    )
                    if clicks[0] and not clicked:
                        scrollCounterS += 1
            if scrollCounterS > 0:
                screen.blit(pygame.transform.scale(upArrowImg, (70, 70)), (1325, 150))
                if upArrowButtonS.collidepoint(mousePos):
                    screen.blit(
                        pygame.transform.scale(upArrowImgPressed, (70, 70)), (1325, 150)
                    )
                    if clicks[0] and not clicked:
                        scrollCounterS -= 1

    if showFilename:
        textBox = pygame.rect.Rect((660, 650, 250, 70))
        drawText(screen, Dispfilename, "black", textBox, fontFileName)


run = True
while run:
    timer.tick(fps)
    mousePos = pygame.mouse.get_pos()

    if menu:
        drawMenu()

    if menu2:
        drawMenu2()
        centerMenu = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False
        if event.type == pygame.MOUSEWHEEL:
            if (100 < mousePos[0] < 625) and (175 < mousePos[1] < 595):
                if event.y == -1:
                    scrollT = "down"
                else:
                    scrollT = "up"
            if (775 < mousePos[0] < 1300) and (175 < mousePos[1] < 595):
                if event.y == -1:
                    scrollS = "down"
                else:
                    scrollS = "up"
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     transcriptRect = pygame.rect.Rect((100, 175, 525, 420))
        #     if transcriptRect.collidepoint(event.pos):
        #         TextBoxTranscriptActive = True
        #     else:
        #         TextBoxTranscriptActive = False
        #     summaryRect = pygame.rect.Rect((775, 175, 525, 420))
        #     if summaryRect.collidepoint(event.pos):
        #         TextBoxSummaryActive = True
        #     else:
        #         TextBoxSummaryActive = False
        # if event.type == pygame.KEYDOWN and TextBoxTranscriptActive:
        #     if event.key == pygame.K_BACKSPACE:
        #         transcript = transcript[:-1]
        #     else:
        #         transcript += str(event.unicode)
        # if event.type == pygame.KEYDOWN and TextBoxSummaryActive:
        #     if event.key == pygame.K_BACKSPACE:
        #         summary = summary[:-1]
        #     else:
        #         summary += str(event.unicode)
    pygame.display.flip()
pygame.quit()
