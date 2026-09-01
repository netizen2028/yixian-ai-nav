/**
 * @Author: chentong
 * @Date: 2024/05/26 上午1:46
 */

package index

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	v1 "github.com/ch3nnn/webstack-go/api/v1"
)

func (h *Handler) Index(ctx *gin.Context) {
	// ?category=N 用于 SEO（标题 / canonical / JSON-LD）与前端锚点定位
	categoryID := 0
	if raw := ctx.Query("category"); raw != "" {
		if n, err := strconv.Atoi(raw); err == nil && n > 0 {
			categoryID = n
		}
	}

	resp, err := h.indexService.Index(ctx, categoryID)
	if err != nil {
		v1.HandleError(ctx, http.StatusInternalServerError, err, nil)
		return
	}

	ctx.HTML(http.StatusOK, "index.html", resp)
}
